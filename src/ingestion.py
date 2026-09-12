"""
Ingestion — Step "before Step 0" in practice: turns a folder containing the
input workbook + raw session/component docx files into a structured
IngestedPackage (schema.py), written to working/ingested.json.

Deliberately generic: tables are located by matching header text, not by
hardcoded cell coordinates, so this doesn't break the moment a real firm's
workbook adds a column or reorders tabs.
"""

import argparse
import glob
import os
import re
from typing import Optional

import openpyxl
from docx import Document as DocxDocument

from schema import (
    EngagementMetadata, TeamMember, Component, DiscussionSession,
    ComponentFraudRiskInput, KnownSuspectedFraudIncident,
    WhistleblowerHotlineEntry, PriorYearExcerpt, IngestedPackage,
)


def _norm(s):
    return str(s).strip().lower() if s is not None else ""


def find_header_row(ws, header_names, max_row=200):
    """Return the row index whose cells match header_names (case-insensitive,
    in order, starting at some column), or None."""
    wanted = [_norm(h) for h in header_names]
    for row in ws.iter_rows(min_row=1, max_row=min(max_row, ws.max_row)):
        vals = [_norm(c.value) for c in row]
        for start_col in range(len(vals)):
            window = vals[start_col:start_col + len(wanted)]
            if window == wanted:
                return row[0].row, start_col + 1  # 1-indexed column of first header
    return None, None


def read_table(ws, header_names):
    """Locate a table by its header row, then read rows until a fully blank
    row. Returns a list of dicts keyed by header_names."""
    header_row, start_col = find_header_row(ws, header_names)
    if header_row is None:
        return []
    rows = []
    r = header_row + 1
    while r <= ws.max_row:
        vals = [ws.cell(row=r, column=start_col + i).value for i in range(len(header_names))]
        if all(v is None or str(v).strip() == "" for v in vals):
            break
        rows.append(dict(zip(header_names, vals)))
        r += 1
    return rows


def read_key_value_block(ws, keys, max_row=100):
    """For the Engagement Metadata tab: scan for cells matching each key
    (case-insensitive) in column B-ish, return {key: value_in_next_cell}."""
    out = {}
    wanted = {k.lower(): k for k in keys}
    for row in ws.iter_rows(min_row=1, max_row=min(max_row, ws.max_row)):
        for i, cell in enumerate(row):
            if cell.value and _norm(cell.value) in wanted:
                # value is the next non-empty cell to the right
                for j in range(i + 1, len(row)):
                    if row[j].value not in (None, ""):
                        out[wanted[_norm(cell.value)]] = row[j].value
                        break
    return out


def _parse_engagement_year(v) -> str:
    """Robust against explanatory parentheticals like
    'recurring (... first-year procedures not applicable)' — a naive
    substring search for 'first-year' on that exact real-world phrasing
    would wrongly classify a recurring engagement as first-year. Match on
    the leading word only."""
    s = _norm(v)
    if re.match(r"^\s*first[\s-]?year\b", s):
        return "first-year"
    return "recurring"


def _to_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    s = _norm(v)
    return s.startswith("true") or s.startswith("yes")


def parse_engagement_metadata(wb) -> EngagementMetadata:
    ws = wb["Engagement Metadata"]
    keys = ["client_name", "primary_framework", "industry", "fiscal_year_end",
            "complexity_tier", "public_interest_entity", "engagement_year",
            "cyber_exposure_flag", "going_concern_indicator", "prior_year_findings"]
    kv = read_key_value_block(ws, keys)

    team_ws = wb["Team & Components"]
    team_rows = read_table(team_ws, ["Name", "Role"])
    comp_rows = read_table(team_ws, ["Component", "Relationship", "Materiality Basis", "Notes"])

    team_members = [TeamMember(name=r["Name"], role=r["Role"]) for r in team_rows]
    components = []
    for r in comp_rows:
        rel_raw = str(r["Relationship"])
        relationship = "network-firm" if "network-firm" in rel_raw.lower() and "other" not in rel_raw.lower() else (
            "other-firm" if "other-firm" in rel_raw.lower() else rel_raw)
        components.append(Component(name=r["Component"], materiality_basis=r["Materiality Basis"],
                                     relationship=relationship))

    return EngagementMetadata(
        client_name=str(kv.get("client_name", "")).strip(),
        primary_framework=str(kv.get("primary_framework", "")).strip(),
        industry=str(kv.get("industry", "")).strip(),
        fiscal_year_end=str(kv.get("fiscal_year_end", "")).strip(),
        complexity_tier=str(kv.get("complexity_tier", "")).strip().lower(),
        public_interest_entity=_to_bool(kv.get("public_interest_entity", False)),
        engagement_year=_parse_engagement_year(kv.get("engagement_year", "")),
        cyber_exposure_flag=_to_bool(kv.get("cyber_exposure_flag", False)),
        going_concern_indicator=_to_bool(kv.get("going_concern_indicator", False)),
        team_members=team_members,
        components=components,
        prior_year_findings=str(kv.get("prior_year_findings", "")).strip() or None,
    )


def parse_incidents(wb):
    if "Known-Suspected Fraud Log" not in wb.sheetnames:
        return []
    rows = read_table(wb["Known-Suspected Fraud Log"],
                       ["entry_id", "description", "date_identified", "source", "status"])
    return [KnownSuspectedFraudIncident(
        entry_id=str(r["entry_id"]), description=str(r["description"]),
        date_identified=str(r["date_identified"]), source=str(r["source"]),
        status=str(r["status"])) for r in rows]


def parse_hotline(wb):
    if "Whistleblower Hotline Log" not in wb.sheetnames:
        return []
    rows = read_table(wb["Whistleblower Hotline Log"], ["date_logged", "complaint_summary", "disposition"])
    return [WhistleblowerHotlineEntry(date_logged=str(r["date_logged"]),
                                       complaint_summary=str(r["complaint_summary"]),
                                       disposition=str(r["disposition"])) for r in rows]


def parse_prior_year_excerpt(wb):
    if "Prior-Year Memo Excerpt" not in wb.sheetnames:
        return []
    ws = wb["Prior-Year Memo Excerpt"]
    text_parts = []
    topic_id = "D1"
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str):
                m = re.match(r"Topic\s+([A-Z]\d+)", cell.value)
                if m:
                    topic_id = m.group(1)
                elif cell.value.strip().startswith('"'):
                    text_parts.append(cell.value.strip())
    if not text_parts:
        return []
    return [PriorYearExcerpt(topic_id=topic_id, text=" ".join(text_parts))]


def parse_session_log(wb):
    ws = wb["Session Log"]
    session_rows = read_table(ws, ["session_id", "session_type", "trigger_source",
                                    "discussion_date", "attendees", "raw_notes_file"])
    comp_input_rows = read_table(ws, ["Component", "Relationship", "Discussion Date",
                                       "Status", "Document", "adequacy_review_status"])
    return session_rows, comp_input_rows


def read_docx_text(path) -> str:
    doc = DocxDocument(path)
    parts = []
    for p in doc.paragraphs:
        if p.text.strip():
            parts.append(p.text.strip())
    return "\n".join(parts)


def build_sessions(session_rows, input_dir):
    sessions = []
    for r in session_rows:
        fname = str(r["raw_notes_file"]).strip()
        fpath = os.path.join(input_dir, fname)
        raw_text = read_docx_text(fpath) if os.path.exists(fpath) else ""
        attendees = [a.strip() for a in str(r["attendees"]).split(",")] if r.get("attendees") else []
        trig = r.get("trigger_source")
        trig = None if trig in (None, "", "—") else str(trig)
        sessions.append(DiscussionSession(
            session_id=str(r["session_id"]),
            session_type=str(r["session_type"]).strip().lower(),
            discussion_date=str(r["discussion_date"]),
            attendees=attendees,
            raw_notes=raw_text,
            trigger_source=trig,
            source_file=fname,
        ))
    return sessions


def build_component_inputs(comp_input_rows, input_dir):
    out = []
    for r in comp_input_rows:
        doc_name = r.get("Document")
        received = bool(doc_name) and str(doc_name).strip() not in ("", "— none —")
        notes = ""
        if received:
            fpath = os.path.join(input_dir, str(doc_name).strip())
            if os.path.exists(fpath):
                notes = read_docx_text(fpath)
        rel_raw = str(r.get("Relationship", ""))
        relationship = "network-firm" if "network-firm" in rel_raw.lower() else (
            "other-firm" if "other-firm" in rel_raw.lower() else rel_raw)
        out.append(ComponentFraudRiskInput(
            component_name=str(r["Component"]),
            component_auditor="",  # not separately tracked in the Session Log tab; component doc itself may state it
            relationship=relationship,
            discussion_date=str(r.get("Discussion Date")) if r.get("Discussion Date") not in (None, "—") else None,
            topic_coverage_notes=notes or None,
            adequacy_review_status=str(r.get("adequacy_review_status", "not required")),
            received=received,
        ))
    return out


def ingest(input_dir: str, output_path: str) -> IngestedPackage:
    xlsx_matches = glob.glob(os.path.join(input_dir, "*.xlsx"))
    if not xlsx_matches:
        raise FileNotFoundError(f"No .xlsx input workbook found in {input_dir}")
    wb = openpyxl.load_workbook(xlsx_matches[0], data_only=True)

    metadata = parse_engagement_metadata(wb)
    session_rows, comp_input_rows = parse_session_log(wb)
    sessions = build_sessions(session_rows, input_dir)
    component_inputs = build_component_inputs(comp_input_rows, input_dir)
    incidents = parse_incidents(wb)
    hotline_entries = parse_hotline(wb)
    prior_year_excerpts = parse_prior_year_excerpt(wb)

    package = IngestedPackage(
        metadata=metadata,
        sessions=sessions,
        component_inputs=component_inputs,
        incidents=incidents,
        hotline_entries=hotline_entries,
        prior_year_excerpts=prior_year_excerpts,
    )
    package.to_json(output_path)
    return package


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ingest a Fraud Risk Brainstorming input package")
    ap.add_argument("input_dir", help="Folder containing the input workbook + session/component docx files")
    ap.add_argument("-o", "--output", default="working/ingested.json")
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    pkg = ingest(args.input_dir, args.output)
    print(f"Ingested: {pkg.metadata.client_name} — {len(pkg.sessions)} sessions, "
          f"{len(pkg.component_inputs)} component inputs, {len(pkg.incidents)} incidents, "
          f"{len(pkg.hotline_entries)} hotline entries -> {args.output}")
