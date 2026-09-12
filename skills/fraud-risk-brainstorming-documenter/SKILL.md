---
name: fraud-risk-brainstorming-documenter
description: >
  Turns a fraud-discussion input package (session notes, component fraud
  discussion summaries, incident logs) into an ISA 240-compliant Fraud Risk
  Brainstorming Memo, Fraud Risk Register, Escalation Log, and pre-session
  checklists. Use when someone asks to document, draft, or structure a
  fraud brainstorming / fraud risk discussion, an ISA 240 or PCAOB AS 2401
  engagement team fraud discussion, or asks to "run the fraud risk
  brainstorming documenter." Requires the fraud-risk-brainstorming-documenter
  repo (or an equivalent checkout with src/cli.py, src/topics_catalog.py,
  src/schema.py) to be available in the working directory.
---

# Fraud Risk Brainstorming Documenter

Full methodology: `docs/Fraud-Risk-Brainstorming-Documenter_Skill-Workflow-Spec.md`
Data contract: `docs/Fraud-Risk-Brainstorming-Documenter_IO-Spec.md`
Full operating sequence with exact commands: `CLAUDE.md` at the repo root —
**read that file before running anything**, it has the CLI invocations and
the JSON schemas this skill produces at each step.

## What this skill does

1. Ingests a workbook + raw session/component `.docx` files into structured
   JSON (deterministic — `src/cli.py ingest`)
2. **You read the raw notes yourself** and judge each mandatory topic's
   coverage status — this is the one step that is not a script (see
   CLAUDE.md §2 for exactly what to produce and the calibration rules)
3. Runs the boilerplate/staleness check, then the deterministic hard-gate
   and graduated-flag rules (`src/cli.py boilerplate`, `src/cli.py flag`)
4. Exports the Memo, Register, Escalation Log, checklists, and cross-tool
   handoff JSON (`src/cli.py export`)

## When NOT to use this

- Performing the fraud risk *assessment* itself (risk ratings, significance
  designation) — that's the Risk Assessment Memo Generator's job
- Testing journal entries for management override — that's the JE Testing
  & Anomaly Screener's job
- Anything requiring legal judgment on whether a suspected fraud disclosure
  is substantiated, or what a required regulatory communication should say

## Non-negotiables

- Every "Evidenced" topic status must trace to an actual excerpt from the
  raw notes — never infer coverage from a topic being generally relevant
- A hard gate that's genuinely open (missing component input, unresolved
  investigation, EQR not logged) stays open — don't paper over it to reach
  a clean "Final" memo. A DRAFT-status output that's honest is the correct
  and expected result for many real engagements at any given point in time.
