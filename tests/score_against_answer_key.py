"""
Scores a completed run's working/topic_coverage.json + working/flags.json
against the conditions deliberately built into sample_input/ (documented
human-readably in that workbook's Test_Scenarios_Answer_Key tab).

This is a regression check for the deterministic parts of the pipeline
(flag_engine.py, boilerplate.py, topics_catalog.py) — it does NOT grade the
quality of the topic-coverage judgment itself (that's Claude Code's job,
not machine-checkable). A clean score here means "the rules still fire the
way they did when this fixture was built," not "this is a good memo."
"""

import argparse
import json
import sys


def _topic(records, topic_id):
    for r in records:
        if r["topic_id"] == topic_id:
            return r
    return None


def _any_contains(items, *substrings):
    return any(all(s.lower() in item.lower() for s in substrings) for item in items)


def run_checks(topic_records, flags):
    checks = []

    def check(name, condition):
        checks.append((name, bool(condition)))

    hard_gates = flags["hard_gates"]
    graduated = flags["graduated_flags"]
    changelog_items = [c["item"] for c in flags["changelog"]]

    # --- Overall ---
    check("Overall: memo_status is DRAFT (package cannot cleanly finalize)",
          flags["memo_status"] != "Final")
    check("Overall: at least 3 hard gates remain open",
          len(hard_gates) >= 3)

    # --- B1 ---
    b1 = _topic(topic_records, "B1")
    check("B1: status is Evidenced", b1 and b1["status"] == "Evidenced")
    check("B1: rebuttal-not-stream-specific graduated flag present",
          _any_contains(graduated, "B1", "not tied to a specific revenue stream"))

    # --- B2 ---
    b2 = _topic(topic_records, "B2")
    check("B2: status is Evidenced (sourced from a later session, not fabricated onto planning)",
          b2 and b2["status"] == "Evidenced" and b2.get("source_session_id") != "S1")
    check("B2: not a hard gate in the final cumulative state",
          not _any_contains(hard_gates, "B2 not evidenced"))

    # --- D1 / boilerplate ---
    d1 = _topic(topic_records, "D1")
    check("D1: boilerplate_flag is True", d1 and d1.get("boilerplate_flag") is True)
    check("D1: boilerplate graduated flag present",
          _any_contains(graduated, "D1", "boilerplate"))
    check("D1: remediation-status-not-stated graduated flag present",
          _any_contains(graduated, "D1", "remediation status not stated"))

    # --- C1/C2/C3 skew ---
    c1 = _topic(topic_records, "C1")
    check("C1: status is Evidenced", c1 and c1["status"] == "Evidenced")
    check("Fraud-triangle skew graduated flag present",
          _any_contains(graduated, "skewed to one factor"))

    # --- Escalation / EQR ---
    check("Hard gate: Distribution Pacific missing component input",
          _any_contains(hard_gates, "Distribution", "Pacific", "no Component Fraud Risk Input"))
    check("Hard gate: FinPay other-firm adequacy review not completed",
          _any_contains(hard_gates, "FinPay", "adequacy review not completed"))
    check("Hard gate: EQR checkpoint required but not logged",
          _any_contains(hard_gates, "EQR checkpoint required"))

    # --- F3 / I1 calibration ---
    f3 = _topic(topic_records, "F3")
    check("F3: status is Partially evidenced (not over-credited to Evidenced)",
          f3 and f3["status"] == "Partially evidenced")
    i1 = _topic(topic_records, "I1")
    check("I1: status is Partially evidenced (passing mention isn't 'Evidenced')",
          i1 and i1["status"] == "Partially evidenced")

    # --- H2 still open ---
    h2 = _topic(topic_records, "H2")
    check("H2: still-open-at-final qualifier or graduated flag present",
          (h2 and "still_open_at_final" in h2.get("qualifier_flags", [])) or
          _any_contains(graduated, "H2", "open item"))

    # --- J1/J4 (organically discovered gaps — regression-guard once found) ---
    j1 = _topic(topic_records, "J1")
    check("J1: status is Not evidenced (group never pushed its own risk factors outward)",
          j1 and j1["status"] == "Not evidenced")
    j4 = _topic(topic_records, "J4")
    check("J4: status is Not evidenced (top-side/consolidating entries distinct from B2)",
          j4 and j4["status"] == "Not evidenced")

    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sample_input_dir", help="Unused directly (checks are Python-coded), kept for CLI symmetry")
    ap.add_argument("topic_coverage_json")
    ap.add_argument("flags_json")
    args = ap.parse_args()

    with open(args.topic_coverage_json) as f:
        topic_records = json.load(f)
    with open(args.flags_json) as f:
        flags = json.load(f)

    results = run_checks(topic_records, flags)
    passed = sum(1 for _, ok in results if ok)
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    print(f"\n{passed}/{len(results)} checks passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
