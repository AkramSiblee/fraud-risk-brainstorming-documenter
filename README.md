# Fraud Risk Brainstorming Documenter

Structures the ISA 240 / PCAOB AS 2401 / AU-C 240 mandatory engagement team
fraud discussion into audit-ready documentation: a pre-session checklist,
a Fraud Risk Brainstorming Memo, a Fraud Risk Register, and an
access-restricted Escalation Log — built from raw session notes across the
full audit lifecycle (planning, interim, final, and ad-hoc trigger-based
re-discussions), including group/component engagements.

## Setup

New machine with nothing installed yet (VS Code, Node, Python, Claude Code)?
See **`SETUP.md`** for the full first-time install walkthrough. If those are
already installed:

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

## FAQ

**What is this agent for?**
It turns the raw notes from an engagement team's mandatory ISA 240 / PCAOB
AS 2401 / AU-C 240 fraud discussion into finished deliverables: a Fraud Risk
Brainstorming Memo, a Fraud Risk Register, an access-restricted Escalation
Log, and pre-session checklists. Claude Code does the reading-comprehension
judgment (did the team actually, meaningfully discuss each required topic);
deterministic Python code does the parsing, rule-based flagging, and
Word/Excel generation.

**Where do I put my input files?**
In a new folder of their own, e.g. `sample_input/<client_name>/`, alongside
the two example folders. That folder needs exactly one `.xlsx` workbook
(Engagement Metadata, Team & Components, Session Log, Known/Suspected Fraud
Log, Whistleblower Hotline Log, and Prior-Year Memo Excerpt tabs) plus one
`.docx` file per session/component, named as referenced in the Session Log
tab. Use `sample_input/thornbury/` or `sample_input/castellan/` as a
template for the tab/column layout.

**How do I actually provide the input to the agent?**
Run `python src/cli.py ingest <your_folder> -o working/ingested.json`, then
tell Claude Code to continue — it reads `CLAUDE.md` and works through the
rest of the operating sequence automatically (topic-coverage judgment,
boilerplate check, flagging, export).

**Where does the output get saved?**
`output/` at the repo root, once you run the `export` CLI step: the memo
(`.docx`), the Fraud Risk Register (`.xlsx`), the Escalation Log (`.xlsx`),
one checklist per session type (`.docx`), and the two cross-tool handoff
JSON files. `output/` and `working/` are both gitignored — they're
per-engagement local files, not something that gets pushed to GitHub.

**Does any of my data leave my machine?**
No Anthropic API key is used anywhere in this pipeline. The judgment step
runs as Claude Code itself (the agent you're already talking to), not a
separate API call — see the "Division of labor" section of `CLAUDE.md`.

**What format do my session notes need to be in?**
Format-agnostic — plain text, bullet points, or a transcript, as long as
it's a `.docx` file referenced by the Session Log tab. There's no required
template for the notes themselves; the agent reads for content, not layout.

**Is the output ready to hand to the audit team as-is?**
Not without a human read-through. Step 6 of `CLAUDE.md` requires opening the
generated memo, checking every "Evidenced" line traces to a real excerpt,
and confirming the hard gates in the Open Items section make sense — then
reporting the memo's status (Draft vs. Final) to the team. A memo is
watermarked DRAFT automatically if any hard gate is still open.

**What's a "hard gate" vs. a "flag"?**
Hard gates block the memo from being marked Final (e.g. no final session
logged, a known incident never routed for review) — see Skill-Workflow-Spec
§8. Graduated flags surface calibration concerns (a thin rebuttal, a topic
only mentioned in passing) without blocking sign-off. Both are computed
deterministically by `src/flag_engine.py` from what you and the notes
actually recorded — never inferred or guessed.

**Can I run this on a real engagement, not just the two sample fixtures?**
Yes — that's the intended use. `sample_input/thornbury/` and
`sample_input/castellan/` exist only to validate the pipeline (and to show
you the expected input layout); a real engagement is just another folder
under `sample_input/` (or anywhere you point `ingest` at) with your own
workbook and session notes.

**I changed something in `src/` — how do I check I didn't break anything?**
See "Testing a pipeline change" above — score both fixtures, not just one;
they deliberately exercise different code paths (group/recurring/ISA vs.
single-entity/first-year/PCAOB).
