# Fraud Risk Brainstorming Documenter

Structures the ISA 240 / PCAOB AS 2401 / AU-C 240 mandatory engagement team
fraud discussion into audit-ready documentation: a pre-session checklist,
a Fraud Risk Brainstorming Memo, a Fraud Risk Register, and an
access-restricted Escalation Log — built from raw session notes across the
full audit lifecycle (planning, interim, final, and ad-hoc trigger-based
re-discussions), including group/component engagements.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running it

Open this folder in VS Code, then open Claude Code and just ask it to run
the pipeline against an input package — **`CLAUDE.md`** has the full
operating sequence and Claude Code reads it automatically. In short:

```bash
python src/cli.py ingest sample_input/thornbury -o working/ingested.json
# → Claude Code reads working/ingested.json and writes
#   working/topic_coverage.json, working/register_rows.json,
#   working/escalation_fields.json (see CLAUDE.md §2)
python src/cli.py boilerplate --ingested working/ingested.json --topic-coverage working/topic_coverage.json
python src/cli.py flag --ingested working/ingested.json --topic-coverage working/topic_coverage.json --escalation-fields working/escalation_fields.json -o working/flags.json
python src/cli.py export --ingested working/ingested.json --topic-coverage working/topic_coverage.json --flags working/flags.json --register working/register_rows.json --escalation-fields working/escalation_fields.json -o output
```

## What's in this repo

```
docs/            Full methodology (Skill-Workflow-Spec) and data contract (IO-Spec)
skills/          Portable Claude Skill version, installable independent of this repo
src/             The pipeline: ingestion, topics catalog, schema, boilerplate check,
                 flag engine, framework_terms (ISA/PCAOB/AU-C terminology + citations),
                 CLI, and export/ (memo, register, escalation log, checklist, handoffs)
sample_input/thornbury/   Group, recurring, ISA fixture — exercises the J-block,
                 boilerplate detection, thin/bad-rebuttal and fraud-triangle-skew cases
sample_input/castellan/   Single-entity, first-year, PCAOB fixture — exercises the
                 K-block, PCAOB terminology, missing-attendee/incident-routing/
                 required-session hard gates, and the "good content" calibration cases
sample_input/*/worked_example/   Each fixture's validated topic_coverage.json /
                 register_rows.json / escalation_fields.json / flags.json, plus that
                 fixture's full generated output — copy into working/ to skip the
                 judgment step when testing a code change
tests/           score_against_answer_key.py (Thornbury) and score_castellan_answer_key.py
                 (Castellan) — each grades a run against that fixture's built-in answer key
working/         Scratch space for a given engagement's intermediate JSON files (gitignored)
output/          Where a run's deliverables land (gitignored)
```

## Testing a pipeline change

```bash
python tests/score_against_answer_key.py sample_input/thornbury working/topic_coverage.json working/flags.json
python tests/score_castellan_answer_key.py sample_input/castellan working/topic_coverage.json working/flags.json
```

Test against both — they exercise different branches (group/recurring/ISA
vs. single-entity/first-year/PCAOB), and this checks structural regressions
only, not whether the actual memo output reads well.

## Cross-tool handoffs

This tool exports two files other automations in the same audit suite
consume directly — see `output/handoff_je_testing_agent.json` and
`output/handoff_risk_assessment_memo_generator.json`, and IO-Spec §5.6–5.7
for the schema.
