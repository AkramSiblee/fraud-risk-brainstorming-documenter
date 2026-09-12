"""
Flag engine — Skill-Workflow-Spec §8 (Two-Tier Flagging Framework), applied
deterministically. This is intentionally dumb: every rule here reads directly
off structured fields (session metadata, topic status, component records,
incident/escalation records) — the *judgment* about what a topic's status or
qualifier should be already happened in the topic-coverage step (Claude's
job). This module never re-reads raw notes text.
"""

import argparse
import json
import os
import sys

from schema import IngestedPackage, TopicCoverageRecord, load_json_list
from framework_terms import terms_for


def _topics_by_id(topic_records):
    return {t.topic_id: t for t in topic_records}


def evaluate(ingested: IngestedPackage, topic_records: list, escalation_fields: dict,
             eqr_logged: bool = False):
    hard_gates = []
    graduated_flags = []
    changelog = []

    by_id = _topics_by_id(topic_records)

    # --- Hard gate: session documentation (ISA 240.44) ---
    for s in ingested.sessions:
        if not s.discussion_date or not s.attendees:
            hard_gates.append(
                f"Session {s.session_id} ({s.session_type}) is missing a discussion date or attendee "
                f"list — ISA 240.44 documentation requirement"
            )

    # --- Hard gate: framework / complexity tier resolved ---
    if not ingested.metadata.primary_framework:
        hard_gates.append("primary_framework not resolved (Step 0)")
    if ingested.metadata.complexity_tier not in ("single-entity", "group"):
        hard_gates.append("complexity_tier not resolved (Step 0)")

    # --- Hard gate: B1 / B2 not evidenced at all ---
    for tid in ("B1", "B2"):
        rec = by_id.get(tid)
        if rec is None or rec.status == "Not evidenced":
            hard_gates.append(f"{tid} not evidenced in any session logged to date")

    # --- Hard gate: group component coverage + other-firm adequacy review ---
    if ingested.metadata.complexity_tier == "group":
        listed = {c.name for c in ingested.metadata.components}
        received = {c.component_name for c in ingested.component_inputs if c.received}
        for missing in sorted(listed - received):
            hard_gates.append(f"Component '{missing}' has no Component Fraud Risk Input on file")
        for ci in ingested.component_inputs:
            if ci.received and ci.relationship == "other-firm" and \
                    not ci.adequacy_review_status.strip().lower().startswith("reviewed — sufficient"):
                hard_gates.append(
                    f"Other-firm component '{ci.component_name}' adequacy review not completed "
                    f"(status: {ci.adequacy_review_status})"
                )

    # --- Hard gate: known/suspected fraud not yet routed through the Escalation Log ---
    for inc in ingested.incidents:
        if inc.entry_id not in escalation_fields:
            hard_gates.append(f"{inc.entry_id} not yet routed through the Escalation Log (Step 6)")

    # --- Hard gate: EQR checkpoint ---
    # Status fields are descriptive prose ("resolved — internal audit
    # investigated..."), not a bare enum value — an exact-equality check
    # against "resolved" would never match real data and silently count
    # every incident as open. Match on the leading word instead.
    open_incidents = [i for i in ingested.incidents if not i.status.strip().lower().startswith("resolved")]
    if (ingested.metadata.public_interest_entity or open_incidents) and not eqr_logged:
        reasons = []
        if ingested.metadata.public_interest_entity:
            reasons.append("public-interest entity")
        if open_incidents:
            reasons.append(f"{len(open_incidents)} open Escalation Log entr{'y' if len(open_incidents)==1 else 'ies'}")
        hard_gates.append(f"EQR checkpoint required ({', '.join(reasons)}) but not yet logged")

    # --- Hard gate: required session types present ---
    session_types = {s.session_type for s in ingested.sessions}
    for required in ("planning", "final"):
        if required not in session_types:
            hard_gates.append(f"Required '{required}' session not yet logged")

    # --- Graduated flags ---
    for rec in topic_records:
        if rec.status == "Partially evidenced":
            snippet = (rec.supporting_excerpt or "")[:140]
            graduated_flags.append(f"{rec.topic_id}: evidenced but thin — \"{snippet}\"")
        if "rebuttal_not_stream_specific" in rec.qualifier_flags:
            graduated_flags.append(f"{rec.topic_id}: rebuttal recorded but not tied to a specific revenue stream")
        if "remediation_status_not_stated" in rec.qualifier_flags:
            graduated_flags.append(f"{rec.topic_id}: prior-year finding referenced but remediation status not stated")
        if "no_independent_review_followup" in rec.qualifier_flags:
            graduated_flags.append(f"{rec.topic_id}: EUC/spreadsheet risk noted but never followed up for independent review")
        if "still_open_at_final" in rec.qualifier_flags:
            graduated_flags.append(f"{rec.topic_id}: remains an open item even at the final session")
        if "mentioned_not_substantively_discussed" in rec.qualifier_flags:
            graduated_flags.append(f"{rec.topic_id}: mentioned in passing but not substantively discussed as a bias/fraud risk indicator")
        if rec.boilerplate_flag:
            graduated_flags.append(f"{rec.topic_id}: current-year excerpt is a near-verbatim match to the prior-year excerpt (boilerplate)")

    # --- Graduated flag: fraud-triangle coverage skewed to one factor ---
    c_ids = ("C1", "C2", "C3")
    c_status = {t: (by_id[t].status if t in by_id else "Not evidenced") for t in c_ids}
    evidenced = [t for t, s in c_status.items() if s == "Evidenced"]
    not_evidenced = [t for t, s in c_status.items() if s == "Not evidenced"]
    if evidenced and not_evidenced and len(evidenced) < len(c_ids):
        graduated_flags.append(
            f"Fraud-triangle coverage skewed to one factor — {', '.join(evidenced)} evidenced, "
            f"{', '.join(not_evidenced)} not evidenced for the same risk area"
        )

    # --- Graduated flag: PCAOB expects partner participation at each session ---
    fw = terms_for(ingested.metadata.primary_framework)
    if fw["partner_participation_expected"]:
        for s in ingested.sessions:
            if s.attendees and not any("partner" in a.lower() for a in s.attendees):
                graduated_flags.append(
                    f"Session {s.session_id} ({s.session_type}): this framework expects engagement-partner "
                    f"participation, but no attendee is listed as Partner"
                )

    # --- Changelog: every mandatory topic genuinely Not evidenced ---
    for rec in topic_records:
        if rec.status == "Not evidenced":
            extra = f" ({rec.notes_for_reviewer})" if hasattr(rec, "notes_for_reviewer") and getattr(rec, "notes_for_reviewer", None) else ""
            changelog.append({
                "item": f"{rec.topic_id} not evidenced in any session to date{extra}",
                "status": "Pending — awaiting team confirmation",
                "resolved_by_date": "",
            })

    return {
        "hard_gates": hard_gates,
        "graduated_flags": graduated_flags,
        "changelog": changelog,
        "memo_status": "DRAFT — Open Items Pending" if hard_gates else "Final",
    }


def _load_topic_records(path):
    with open(path) as f:
        raw = json.load(f)
    out = []
    for d in raw:
        d = dict(d)
        extra_notes = d.pop("notes_for_reviewer", None)
        rec = TopicCoverageRecord(
            topic_id=d["topic_id"], category=d["category"], status=d["status"],
            supporting_excerpt=d.get("supporting_excerpt"), source_session_id=d.get("source_session_id"),
            component_source=d.get("component_source"), boilerplate_flag=d.get("boilerplate_flag", False),
            qualifier_flags=d.get("qualifier_flags", []),
        )
        if extra_notes:
            setattr(rec, "notes_for_reviewer", extra_notes)
        out.append(rec)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Evaluate hard gates and graduated flags")
    ap.add_argument("ingested_json")
    ap.add_argument("topic_coverage_json")
    ap.add_argument("--escalation-fields", default=None)
    ap.add_argument("--eqr-logged", action="store_true")
    ap.add_argument("-o", "--output", default="working/flags.json")
    args = ap.parse_args()

    ingested = IngestedPackage.from_json(args.ingested_json)
    topic_records = _load_topic_records(args.topic_coverage_json)
    escalation_fields = {}
    if args.escalation_fields and os.path.exists(args.escalation_fields):
        with open(args.escalation_fields) as f:
            escalation_fields = json.load(f)

    result = evaluate(ingested, topic_records, escalation_fields, eqr_logged=args.eqr_logged)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"memo_status: {result['memo_status']}")
    print(f"hard_gates ({len(result['hard_gates'])}):")
    for h in result["hard_gates"]:
        print("  -", h)
    print(f"graduated_flags ({len(result['graduated_flags'])}):")
    for g in result["graduated_flags"]:
        print("  -", g)
