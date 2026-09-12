# Fraud Risk Brainstorming Documenter — Claude Code Operating Instructions

This repo turns a raw fraud-discussion input package (session notes, component
submissions, incident logs) into a complete ISA 240 Fraud Risk Brainstorming
Memo, Fraud Risk Register, Escalation Log, and pre-session checklists.

**Read `docs/Fraud-Risk-Brainstorming-Documenter_Skill-Workflow-Spec.md` and
`docs/Fraud-Risk-Brainstorming-Documenter_IO-Spec.md` before your first run
on a new engagement.** Those two files are the actual methodology and data
contract — this file is only the operating sequence for executing them.

## Division of labor — important

This pipeline deliberately splits work between deterministic code and you
(Claude Code) directly:

- **Code does**: reading files, computing text similarity, applying the
  hard-gate/graduated-flag rules, generating the Word/Excel outputs. These
  are CLI commands below. Never re-implement this logic yourself — call the
  CLI.
- **You do**: reading the raw session notes and judging, per topic, whether
  it was `Evidenced`, `Partially evidenced`, or `Not evidenced`, and pulling
  the supporting excerpt. This is genuine reading comprehension — a keyword
  search would miss exactly the things a reviewer cares about (e.g. a
  rebuttal that sounds like it addresses revenue recognition but never ties
  to a specific revenue stream). **Never skip this step or approximate it
  with pattern matching** — it's the one part of this pipeline that isn't
  automatable, which is why it isn't a Python script.

No Anthropic API key is used or needed anywhere in this pipeline — the
judgment step is performed by you, running as Claude Code, not by a
separate API call.

## Operating sequence

Run these from the repo root, with a Python virtualenv that has
`requirements.txt` installed.

### 1. Ingest
```
python src/cli.py ingest sample_input/thornbury -o working/ingested.json
```
(or `sample_input/castellan`, or a real engagement's own folder). Reads the input workbook (Engagement Metadata, Team & Components, Session
Log, Known/Suspected Fraud Log, Whistleblower Hotline Log, Prior-Year
Memo Excerpt tabs) plus every session/component `.docx` referenced in the
Session Log tab, into one structured JSON file.

**If ingestion reports zero sessions or an empty `components` list**, don't
proceed — the input workbook doesn't match the expected tab/header
structure. Open it and check header text matches `src/ingestion.py`'s
expected column names before touching the code.

### 2. Topic-coverage judgment (you do this — no CLI command)

Open `working/ingested.json` and `src/topics_catalog.py` (the full
mandatory-topics list, with `applies_if` conditions for the group and
first-year blocks). For every topic in scope given this engagement's
`complexity_tier` and `engagement_year`, read across **all** sessions'
`raw_notes` and decide:

- `status`: `"Evidenced"`, `"Partially evidenced"`, or `"Not evidenced"`
- `supporting_excerpt`: the actual text that supports your call, or `null`
- `source_session_id`: which session first evidenced it — once a topic is
  evidenced, a later session can only add to or update it, never silently
  overwrite a documented status back to "not evidenced"
- `qualifier_flags`: attach any of these string tags where the content
  earns it (see `flag_engine.py` for what each one triggers): 
  `rebuttal_not_stream_specific` (B1's rebuttal isn't tied to a specific
  revenue stream), `remediation_status_not_stated` (D1 references a prior
  finding but never gives a concrete remediation status),
  `no_independent_review_followup` (F3's EUC risk was named but never
  followed up), `still_open_at_final` (a topic remains unresolved even at
  the final session), `mentioned_not_substantively_discussed` (a topic
  surfaces only in passing, not as genuine discussion — this is a
  **calibration check**: don't mark something "Evidenced" just because a
  word for it appears in the notes).

Be honest about calibration. A passing mention is `Partially evidenced` at
best. A topic genuinely never raised is `Not evidenced` — don't infer intent
that isn't in the text. If the group only ever *requested* component input
rather than *communicating its own* fraud risk factors outward, that's a
real J1 gap, not a technicality — flag it.

Write the result as a JSON array to `working/topic_coverage.json`
(schema: `TopicCoverageRecord` in `src/schema.py`). Also produce, at the
same time, from the same reading:

- `working/register_rows.json` — one `FraudRiskRegisterRow` per identified
  fraud risk (not one per topic — several topics can point at the same
  underlying risk). Never invent a `planned_response`; leave it blank for
  the team.
- `working/escalation_fields.json` — for every `KnownSuspectedFraudIncident`
  in `working/ingested.json`, judge `communication_required`,
  `partner_reviewed`, `access_list`, and `standard_file_clearance` from
  what the notes actually say was done. Don't mark something cleared or
  communicated unless a session explicitly says so — an unresolved
  investigation stays unresolved.

### 3. Boilerplate check
```
python src/cli.py boilerplate --ingested working/ingested.json --topic-coverage working/topic_coverage.json
```
Compares each topic's current-year excerpt against the prior year's
excerpt for the same topic and sets `boilerplate_flag` where they're
suspiciously close. This mutates `working/topic_coverage.json` in place —
run it after you've written the file in Step 2, before flagging.

### 4. Flag evaluation
```
python src/cli.py flag --ingested working/ingested.json --topic-coverage working/topic_coverage.json --escalation-fields working/escalation_fields.json -o working/flags.json
```
Deterministically applies every hard gate and graduated flag from
Skill-Workflow-Spec §8. Add `--eqr-logged` only once an actual EQR review
has occurred — never pass it just to clear the gate.

### 5. Export
```
python src/cli.py export --ingested working/ingested.json --topic-coverage working/topic_coverage.json --flags working/flags.json --register working/register_rows.json --escalation-fields working/escalation_fields.json -o output
```
Generates the Memo (docx, watermarked DRAFT if any hard gate is open), the
Fraud Risk Register (xlsx), the Escalation Log (xlsx, restricted-access
tagged), a pre-session checklist for each session type, and the two
cross-tool handoff JSONs (`output/handoff_je_testing_agent.json`,
`output/handoff_risk_assessment_memo_generator.json`).

### 6. Review before handing to the team

Open the generated memo and actually read it — check every "Evidenced"
line traces to a real excerpt, and that the hard gates in the Open Items
section are things a real reviewer would also flag. Report the memo's
status (DRAFT vs Final) and the open items list to the person you're
working with; don't just say "done."

## Validating a change to this pipeline

There are two fixtures, deliberately covering different branches:
- `sample_input/thornbury/` — group, recurring, ISA. Covers the J-block
  (group/component), D1 continuity, boilerplate detection, and a thin/bad
  B1 rebuttal and skewed fraud-triangle coverage.
- `sample_input/castellan/` — single-entity, first-year, PCAOB. Covers the
  K-block (predecessor/opening-balance), PCAOB terminology and the
  partner-participation expectation, the missing-attendee-list hard gate,
  the incident-not-routed hard gate, the required-final-session hard gate,
  and a genuinely good B1 rebuttal / fully-covered fraud triangle (to
  confirm those flags correctly do NOT fire on good content).

If you edit `flag_engine.py`, `boilerplate.py`, `framework_terms.py`, or
`topics_catalog.py`, re-run the full sequence against **both** fixtures and
score against both:
```
python tests/score_against_answer_key.py sample_input/thornbury working/topic_coverage.json working/flags.json
python tests/score_castellan_answer_key.py sample_input/castellan working/topic_coverage.json working/flags.json
```
A change that only gets tested against one fixture is only half-tested —
several real bugs in this pipeline (an EQR count that silently double-counted
resolved incidents, a substring match that misclassified a recurring
engagement as first-year) were only caught once the second fixture forced
a different code path to actually run. Each fixture's `worked_example/`
subfolder has the validated topic_coverage.json / register_rows.json /
escalation_fields.json / flags.json plus that fixture's full generated
output, so you don't have to redo the judgment step just to test a code
change — copy them into `working/` and go straight to `boilerplate` / `flag`
/ `export`.

This is not a substitute for actually reading the memo output — it only
catches structural regressions, not whether a topic-coverage judgment was
sound.

## Guardrails (see Skill-Workflow-Spec §9 for the full list)

- Never fabricate discussion content not present in the raw notes
- Never judge whether a rebuttal or a component's work is *sufficient* —
  record what was said, flag it, and leave the judgment to the partner/EQR
- Never draft the actual TCWG/regulator communication — only flag that one
  is required
- Never rate risk significance or link to overall audit strategy — that's
  the Risk Assessment Memo Generator's job, not this tool's
- Never bypass restricted-access tagging on an Escalation Log entry
