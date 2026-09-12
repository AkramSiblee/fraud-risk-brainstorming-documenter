"""
CLI entrypoint. Deliberately thin — it wires together the deterministic
steps. The topic-coverage judgment step (Step 4 in the Skill-Workflow-Spec)
is NOT a CLI command: that's where Claude Code reads the raw notes in
working/ingested.json against src/topics_catalog.py and writes
working/topic_coverage.json (plus working/register_rows.json and
working/escalation_fields.json) itself. See CLAUDE.md for the full
operating sequence.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "export"))

from schema import IngestedPackage, PriorYearExcerpt
import ingestion
import boilerplate
import flag_engine
from export import build_register, build_escalation_log, build_memo, build_checklist, build_handoffs


def cmd_ingest(args):
    pkg = ingestion.ingest(args.input_dir, args.output)
    print(f"Ingested {pkg.metadata.client_name}: {len(pkg.sessions)} sessions, "
          f"{len(pkg.component_inputs)} component inputs.")


def cmd_boilerplate(args):
    ingested = json.load(open(args.ingested))
    prior = [PriorYearExcerpt(**p) for p in ingested["prior_year_excerpts"]]
    records = flag_engine._load_topic_records(args.topic_coverage)
    boilerplate.apply_boilerplate_check(records, prior, threshold=args.threshold)
    out = []
    for r in records:
        d = {"topic_id": r.topic_id, "category": r.category, "status": r.status,
             "supporting_excerpt": r.supporting_excerpt, "source_session_id": r.source_session_id,
             "component_source": r.component_source, "boilerplate_flag": r.boilerplate_flag,
             "qualifier_flags": r.qualifier_flags}
        if hasattr(r, "notes_for_reviewer"):
            d["notes_for_reviewer"] = r.notes_for_reviewer
        out.append(d)
    json.dump(out, open(args.topic_coverage, "w"), indent=2)
    print(f"Boilerplate check applied (threshold={args.threshold}) -> {args.topic_coverage}")


def cmd_flag(args):
    ingested = IngestedPackage.from_json(args.ingested)
    topic_records = flag_engine._load_topic_records(args.topic_coverage)
    escalation_fields = {}
    if args.escalation_fields and os.path.exists(args.escalation_fields):
        escalation_fields = json.load(open(args.escalation_fields))
    result = flag_engine.evaluate(ingested, topic_records, escalation_fields, eqr_logged=args.eqr_logged)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    json.dump(result, open(args.output, "w"), indent=2)
    print(f"memo_status: {result['memo_status']}  |  hard_gates: {len(result['hard_gates'])}  |  "
          f"graduated_flags: {len(result['graduated_flags'])}")


import re

def _slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def cmd_export(args):
    os.makedirs(args.output_dir, exist_ok=True)
    ingested = IngestedPackage.from_json(args.ingested)
    client_slug = _slugify(ingested.metadata.client_name)

    memo_path = os.path.join(args.output_dir, f"{client_slug}_FraudBrainstorming_Memo.docx")
    build_memo.build(args.ingested, args.topic_coverage, args.flags, args.register, memo_path)
    print("wrote", memo_path)

    if args.register:
        reg_path = os.path.join(args.output_dir, f"{client_slug}_FraudRiskRegister.xlsx")
        build_register.build(args.register, ingested.metadata.client_name, reg_path)
        print("wrote", reg_path)

    if args.escalation_fields:
        esc_path = os.path.join(args.output_dir, f"{client_slug}_EscalationLog.xlsx")
        build_escalation_log.build(args.ingested, args.escalation_fields, ingested.metadata.client_name, esc_path)
        print("wrote", esc_path)

    for session_type in ("planning", "interim", "final"):
        chk_path = os.path.join(args.output_dir, f"{client_slug}_Checklist_{session_type.title()}.docx")
        build_checklist.build(args.ingested, session_type, chk_path)
        print("wrote", chk_path)

    je_path, ramg_path = build_handoffs.build(args.topic_coverage, args.register, args.output_dir)
    print("wrote", je_path)
    print("wrote", ramg_path)


def main():
    ap = argparse.ArgumentParser(prog="fraud-risk-brainstorming-documenter")
    sub = ap.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Read the input package into working/ingested.json")
    p_ingest.add_argument("input_dir")
    p_ingest.add_argument("-o", "--output", default="working/ingested.json")
    p_ingest.set_defaults(func=cmd_ingest)

    p_bp = sub.add_parser("boilerplate", help="Apply the boilerplate/staleness check to topic-coverage records")
    p_bp.add_argument("--ingested", default="working/ingested.json")
    p_bp.add_argument("--topic-coverage", default="working/topic_coverage.json")
    p_bp.add_argument("--threshold", type=float, default=boilerplate.DEFAULT_THRESHOLD)
    p_bp.set_defaults(func=cmd_boilerplate)

    p_flag = sub.add_parser("flag", help="Evaluate hard gates and graduated flags")
    p_flag.add_argument("--ingested", default="working/ingested.json")
    p_flag.add_argument("--topic-coverage", default="working/topic_coverage.json")
    p_flag.add_argument("--escalation-fields", default="working/escalation_fields.json")
    p_flag.add_argument("--eqr-logged", action="store_true")
    p_flag.add_argument("-o", "--output", default="working/flags.json")
    p_flag.set_defaults(func=cmd_flag)

    p_export = sub.add_parser("export", help="Generate the Memo, Register, Escalation Log, Checklists, and handoffs")
    p_export.add_argument("--ingested", default="working/ingested.json")
    p_export.add_argument("--topic-coverage", default="working/topic_coverage.json")
    p_export.add_argument("--flags", default="working/flags.json")
    p_export.add_argument("--register", default="working/register_rows.json")
    p_export.add_argument("--escalation-fields", default="working/escalation_fields.json")
    p_export.add_argument("-o", "--output-dir", default="output")
    p_export.set_defaults(func=cmd_export)

    args = ap.parse_args()
    # normalize dest names used inside the cmd_* functions
    if hasattr(args, "topic_coverage"):
        args.topic_coverage = args.topic_coverage
    args.func(args)


if __name__ == "__main__":
    main()
