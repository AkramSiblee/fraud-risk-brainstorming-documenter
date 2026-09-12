import argparse
import json
import os


B2_J4_KEYWORDS = ("manual", "top-side", "consolidat", "journal")


def build(topic_coverage_json: str, register_rows_json: str, out_dir: str):
    with open(topic_coverage_json, encoding="utf-8") as f:
        topics = json.load(f)
    register_rows = []
    if register_rows_json and os.path.exists(register_rows_json):
        with open(register_rows_json, encoding="utf-8") as f:
            register_rows = json.load(f)

    # --- JE Testing & Anomaly Screener handoff ---
    je_handoff = []
    for t in topics:
        if t["topic_id"] in ("B2", "J4") and t.get("supporting_excerpt"):
            je_handoff.append({
                "risk_area": t["supporting_excerpt"],
                "source_topic_id": t["topic_id"],
                "accounts_implicated": "Manual/top-side journal entries — see memo for detail",
                "timing_window": None,
            })

    # --- Risk Assessment Memo Generator handoff ---
    ramg_handoff = {
        "topic_coverage_record": topics,
        "fraud_risk_register": register_rows,
    }

    os.makedirs(out_dir, exist_ok=True)
    je_path = os.path.join(out_dir, "handoff_je_testing_agent.json")
    ramg_path = os.path.join(out_dir, "handoff_risk_assessment_memo_generator.json")
    with open(je_path, "w", encoding="utf-8") as f:
        json.dump(je_handoff, f, indent=2, ensure_ascii=False)
    with open(ramg_path, "w", encoding="utf-8") as f:
        json.dump(ramg_handoff, f, indent=2, ensure_ascii=False)
    return je_path, ramg_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("topic_coverage_json")
    ap.add_argument("--register", default=None)
    ap.add_argument("-o", "--output-dir", required=True)
    args = ap.parse_args()
    je_path, ramg_path = build(args.topic_coverage_json, args.register, args.output_dir)
    print("wrote", je_path)
    print("wrote", ramg_path)
