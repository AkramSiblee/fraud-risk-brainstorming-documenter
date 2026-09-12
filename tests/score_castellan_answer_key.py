"""
Scores a Castellan pipeline run against the conditions built into
sample_input/castellan/ (see that workbook's Test_Scenarios_Answer_Key tab).

This fixture exists specifically to exercise code paths the Thornbury
fixture never touched: single-entity scope, first-year scope (D1 excluded,
K1/K2 included), PCAOB framework terminology, the missing-attendee-list
hard gate, the incident-not-routed hard gate, the required-final-session
hard gate, and a "good" B1/fraud-triangle case that should NOT raise the
flags a thin one would.
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

    check("Overall: memo_status is DRAFT", flags["memo_status"] != "Final")
    check("Overall: at least 4 hard gates open", len(hard_gates) >= 4)

    # --- Scope exclusions/inclusions ---
    check("D1 absent from topic-coverage records (out of scope for first-year, not 'Not evidenced')",
          _topic(topic_records, "D1") is None)
    check("J1 absent from topic-coverage records (out of scope for single-entity)",
          _topic(topic_records, "J1") is None)
    k1 = _topic(topic_records, "K1")
    check("K1 present and Evidenced (predecessor auditor communication)",
          k1 and k1["status"] == "Evidenced")
    k2 = _topic(topic_records, "K2")
    check("K2 present and Evidenced (opening balance risk)",
          k2 and k2["status"] == "Evidenced")

    # --- Hard gates specific to this fixture ---
    check("Hard gate: S3 missing attendee list",
          _any_contains(hard_gates, "S3", "missing a discussion date or attendee list"))
    check("Hard gate: INC-02 not routed through Escalation Log",
          _any_contains(hard_gates, "INC-02", "not yet routed"))
    check("Hard gate: required final session not logged",
          _any_contains(hard_gates, "final", "not yet logged"))
    check("EQR hard gate correctly counts exactly 1 open incident (not 2)",
          _any_contains(hard_gates, "1 open Escalation Log entry") and
          not _any_contains(hard_gates, "2 open Escalation Log"))

    # --- PCAOB-specific behavior ---
    check("Graduated flag: PCAOB partner-participation expectation not met at S2",
          _any_contains(graduated, "S2", "engagement-partner participation"))
    check("No partner-participation flag raised for S1 (partner was present)",
          not _any_contains(graduated, "S1", "engagement-partner participation"))

    # --- Calibration: flags that should NOT fire on genuinely good content ---
    b1 = _topic(topic_records, "B1")
    check("B1: Evidenced with NO rebuttal-not-specific flag (rebuttal genuinely tied to a specific stream)",
          b1 and b1["status"] == "Evidenced" and "rebuttal_not_stream_specific" not in b1.get("qualifier_flags", []))
    check("No fraud-triangle skew flag (C1/C2/C3 all genuinely covered)",
          not _any_contains(graduated, "skewed to one factor"))
    i1 = _topic(topic_records, "I1")
    check("I1: Evidenced, not Partially evidenced (substantively discussed here, unlike Thornbury)",
          i1 and i1["status"] == "Evidenced")

    # --- Genuine gap this fixture also carries ---
    e2 = _topic(topic_records, "E2")
    check("E2: Not evidenced (hotline never raised)", e2 and e2["status"] == "Not evidenced")

    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sample_input_dir")
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
