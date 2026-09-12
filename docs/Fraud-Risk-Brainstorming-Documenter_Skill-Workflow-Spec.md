---
name: fraud-risk-brainstorming-documenter
description: >
  Structures the ISA 240 / PCAOB AS 2401 / AU-C 240 mandatory engagement team
  fraud discussion into complete, audit-ready documentation across the full
  audit lifecycle — not a single point-in-time memo. Generates framework-aware
  pre-session checklists, parses raw session notes from planning, interim,
  final, and ad-hoc trigger-based re-discussions, and drafts a Fraud Risk
  Brainstorming Memo, Fraud Risk Register, and Escalation Log. Covers
  single-entity, group/component (ISA 600), first-year, and public-interest
  engagements, and hands off structured findings to the JE Testing & Anomaly
  Screener and the Risk Assessment Memo Generator. Never replaces the risk
  assessment itself, the audit response, or the team's judgment — documents
  what was discussed and flags what the standard requires but the notes
  don't evidence.
version: 2.0
owner: [Your Firm/Product Name]
standard_reference: ISA 240, ISA 600 (Revised 2020), ISA 550, ISA 540, ISA 520, AU-C 240, AU-C 600, AU-C 550, AU-C 540, PCAOB AS 2401, PCAOB AS 1215, PCAOB AS 2410
last_updated: 2026-09-11
---

# Fraud Risk Brainstorming Documenter — Skill & Workflow Specification

## 1. Purpose & Scope

### In scope
- Generating a framework-aware pre-session discussion checklist tailored to complexity tier, industry, public/private status, first-year/recurring status, and cyber-exposure profile
- Parsing raw notes from **any discussion session in the audit lifecycle** — planning, interim refresh, final-review refresh, or an ad-hoc session triggered by new information — against the mandatory topics
- Drafting the Fraud Risk Brainstorming Memo and Fraud Risk Register from evidenced discussion content only, carried forward and updated across sessions within one engagement year
- For group engagements: consolidating component-level fraud discussion input per ISA 600, including a group-team adequacy review of each component's input
- Flagging — never silently filling — any mandatory topic the notes don't evidence, and flagging recycled/boilerplate content from the prior year
- Routing any known/suspected fraud disclosure to a separate, access-restricted Escalation Log
- Exporting structured handoff data to the JE Testing & Anomaly Screener (where manual/top-side entry risk was identified) and the Risk Assessment Memo Generator (fraud risk factors feeding the ISA 315 assessment)
- Triggering an Engagement Quality Review (EQR) checkpoint for public-interest entities or any engagement with an open Escalation Log entry

### Out of scope (hard boundary — do not absorb)
- Performing the fraud risk assessment itself — concluding on inherent/control risk ratings or significant-risk designation is the Risk Assessment Memo Generator's job. This tool documents the discussion that feeds that assessment and exports structured findings to it; it does not produce the assessment.
- Designing or evaluating audit responses to identified fraud risks — captured in the register as a placeholder for the team's own response
- Executing JE-level testing for management override — that's the JE Testing & Anomaly Screener's job. This tool exports *where to look* (accounts, entry types, period-end timing) as a scoping input; it does not run the testing.
- Concluding whether a suspected fraud instance is substantiated, or performing any investigation — routes to human/legal review only
- Determining materiality, evaluating the sufficiency of a rebuttal, or judging the adequacy of a component auditor's work — the tool records rebuttal rationale verbatim and flags adequacy-review as a required human step; it does not perform that judgment itself

## 2. Standards Basis

| Requirement | ISA | PCAOB | AU-C | What this tool must capture |
|---|---|---|---|---|
| Engagement team discussion, setting aside prior beliefs about management integrity | 240.15 | AS 2401.05, .52 (brainstorming session) | 240.15 | Attendee list incl. key members; explicit skepticism reminder |
| Susceptibility to fraudulent financial reporting and misappropriation of assets | 240.16, .A11–A22 | AS 2401.14–.18 | 240.16 | Topic coverage by category (§7) |
| Revenue recognition fraud risk — rebuttable presumption | 240.26–27 | AS 2401.54 | 240.27 | Presumption addressed; scheme-level rebuttal rationale, tied to specific revenue streams |
| Management override of controls — always presumed present | 240.31–33 | AS 2401.65 | 240.31 | Presumption addressed regardless of assessed control strength |
| Significant unusual transactions / related parties | 240.A24; ISA 550 | AS 2410; AS 2401.66 | 240.A24; AU-C 550 | Dedicated topic, not an example under "opportunity" |
| Management bias in accounting estimates | 240.A24; ISA 540 | AS 2401.14(.09); AS 2501 | 240.A24; AU-C 540 | Dedicated topic covering key estimates (impairment, ECL/allowance, reserves) |
| Inquiries of management, internal audit, TCWG about fraud | 240.17–18 | AS 2401.20–.28 | 240.17–18 | Confirmation inquiries occurred; responses summarized |
| Unpredictability in nature/timing/extent of procedures | 240.29(c), .A37 | AS 2401.50(f) | 240.29(c) | At least one specific unpredictability element on record |
| Ongoing evaluation / new-information re-discussion | 240.13, .24 | AS 2401.68–.69 | 240.13, .24 | Ad-hoc session type; trigger log |
| Response if fraud or suspected fraud identified | 240.34–38 | AS 2401.70–.83 | 240.34–38 | Routes to Escalation Log, restricted access |
| Communication to management/TCWG/regulators | 240.40–43 | AS 2401.79–.83 | 240.40–43 | Escalation Log "communication required" flag |
| Documentation of the discussion | 240.44 | AS 2401.84 | 240.44 | Date, format, attendees, decisions reached — hard gate |
| Group audits — bidirectional fraud risk communication + adequacy review | ISA 600.31–32, .39 | AS 2101.13 (referred-to auditor concepts) | AU-C 600 | Component input schema; group-team adequacy sign-off; network vs. non-network scrutiny tier |
| First-year audit — predecessor communication, opening balances | ISA 300.A5, ISA 510 | AS 2610, AS 2405 | AU-C 300, AU-C 510 | First-year overlay topic block |

## 3. Framework & Jurisdiction Handling

Detected dynamically from Engagement Metadata (`primary_framework` field), not assumed:

| Framework | Trigger | Key variants applied |
|---|---|---|
| ISA 240 (+ ISA 600/550/540/520) | Non-US, IFRS or local-GAAP audits | "discussion," rebuttable presumption language, group audit per ISA 600 |
| PCAOB AS 2401 | US public company / PCAOB-registered issuer audits | "brainstorming session" terminology; explicit engagement-partner participation expectation; AS 2410 related-party cross-reference; AS 2405 illegal-acts overlay |
| AU-C 240 (+ AU-C 600/550/540) | US private company (AICPA) audits | Largely mirrors ISA with AU-C paragraph citations |

Framework selection changes: mandatory-attendee rules (§5), citation text used in the memo, and which reference block (below) supplies scheme-specific prompts. Framework-specific detail lives in companion reference files, not duplicated inline, so this document stays under the size limit as more frameworks are added:
- `references/isa-240-600.md`
- `references/pcaob-as2401.md`
- `references/auc-240-600.md`

If Engagement Metadata doesn't specify a framework, the tool does not guess — it hard-gates until the framework is confirmed, since attendee rules and citation language differ materially.

## 4. RACI

| Role | Responsibility |
|---|---|
| Engagement Partner | Approves complexity tier and framework, reviews Escalation Log entries, signs off final memo |
| EQR (Engagement Quality Reviewer) | Reviews memo when triggered (§6, Step 9) — public-interest entity or any open Escalation entry |
| Manager | Facilitates each discussion session, owns notes submission, resolves Changelog items |
| Staff / Senior | Contributes session notes; may complete Component Fraud Risk Input for an assigned component |
| Group Engagement Team | Communicates group-level fraud factors to components (H1); performs adequacy review of each component's returned input (H2a) |
| Component Auditor | Submits component-level fraud discussion summary; flags factors for group attention (H3) |
| Automation | Generates checklist, parses notes across sessions, drafts memo/register, flags gaps, exports handoffs — never concludes on risk, adequacy, or authenticity of a fraud allegation |

## 5. Engagement Profile Inputs Driving Dynamism

The checklist and topic set are not static — they scale with:

| Profile flag | Effect |
|---|---|
| `primary_framework` | ISA / PCAOB / AU-C — changes citations, attendee rules, terminology (§3) |
| `complexity_tier` | `single-entity` \| `group` — triggers §7.H and component adequacy review |
| `public_interest_entity` | boolean — triggers mandatory EQR checkpoint (§6, Step 9), heavier related-party and significant-unusual-transaction scrutiny |
| `engagement_year` | `first-year` \| `recurring` — triggers §7.I (predecessor auditor, opening balances) |
| `industry` | pulls from a maintained per-industry fraud-scheme library (e.g., construction: percentage-of-completion manipulation; financial institutions: loan-loss reserve manipulation; SaaS: channel stuffing and capitalized software costs; healthcare: billing/upcoding) rather than a generic 2–3 line prompt |
| `cyber_exposure_flag` | set if client has had a security incident in-year, or handles high-value wire transfers — expands §7.F into BEC/wire-fraud-specific prompts |
| `going_concern_indicator` | boolean — adds an explicit incentive/pressure prompt (going-concern pressure is a classic fraud-incentive amplifier) |

## 6. Execution Steps

**Step 0 — Triage**
Resolve `primary_framework`, `complexity_tier`, `public_interest_entity`, `engagement_year`, and `cyber_exposure_flag` from Engagement Metadata. Missing framework or complexity tier is a hard gate — no checklist generates until resolved.

**Step 1 — Pre-Session: Generate Discussion Checklist**
Build from §7, tailored by every flag in §5. Framework-specific citation text pulled from the relevant reference file (§3). Output: standalone checklist, deliverable before the session — one per session type (see Step 2).

**Step 2 — Session(s) → Notes Capture**
Not a single event. Sessions map to a `session_type`:
- `planning` — required, sets the initial memo
- `interim` — optional refresh, common on longer engagements
- `final` — required refresh per ISA 240.24 / AS 2401.68, considering final analytical procedures and anything that emerged during fieldwork
- `ad-hoc` — triggered by defined events: a whistleblower disclosure, a restatement, a change in senior management, or a fraud indicator surfacing during fieldwork. Each trigger is logged with its source event.
Each session's notes are parsed independently and merged into the cumulative Topic-Coverage Record — a topic evidenced in an earlier session stays evidenced; new sessions can only add or update, never silently overwrite prior evidence.

**Step 3 — Component Fraud Risk Input (group engagements only)**
Each component auditor submits input against the Component Fraud Risk Input schema (io-spec §3.4), tagged `network-firm` or `other-firm`. Other-firm components get an additional group-team adequacy review sub-step (Step 3a) before their input is accepted into consolidation — the group team confirms the component's discussion addressed the mandatory topics at a level of rigor consistent with this methodology, or flags it as insufficient and requests supplementation. The automation never performs the adequacy judgment itself; it only tracks whether the review occurred.

**Step 4 — Topic-Coverage Parsing**
Map each session's notes to every mandatory topic in §7. Status: `Evidenced` / `Partially evidenced` / `Not evidenced`, each with a supporting excerpt or null. Includes a **boilerplate check**: if a topic's supporting excerpt in the current year is a near-verbatim match to the prior year's excerpt for the same client, flag it as a graduated flag ("recycled content — confirm this reflects current-year discussion") rather than accepting it as fresh evidence.

**Step 5 — Draft Memo + Risk Register**
Built cumulatively across all sessions logged so far. Rebuttable-presumption conclusions recorded as stated by the team, with the specificity check in §8. Register rows carry a specific ISA/PCAOB assertion (existence, completeness, valuation, rights & obligations, presentation & disclosure, cutoff) rather than a single free-text "affected" field, so downstream tools can consume it precisely.

**Step 6 — Known/Suspected Fraud Escalation Branch**
Any actual or suspected fraud disclosure (not a hypothetical risk factor) creates an Escalation Log entry, tagged **restricted access** (partner + specifically named reviewers only) and excluded from the standard workpaper file until the partner clears it for standard filing. Notes the ISA 240.40–43 / AS 2401.79–83 communication requirement as unmet until confirmed actioned. Never drafts the communication itself, never assesses substantiation.

**Step 7 — Cross-Tool Handoff Export**
- To the **JE Testing & Anomaly Screener**: exports identified manual-entry, top-side/consolidating-entry, and period-end-timing risk areas as a scoping input (io-spec §5.6) — informs where JE testing samples, does not run the testing
- To the **Risk Assessment Memo Generator**: exports the full Topic-Coverage Record and Fraud Risk Register as an ISA 315 input (io-spec §5.7) — the fraud risk factors identified here feed that tool's inherent-risk-factor analysis; this tool does not itself rate significance

**Step 8 — QA / Pre-Delivery Checklist**
Run io-spec §9 before packaging output.

**Step 9 — EQR Checkpoint (conditional)**
Triggers automatically if `public_interest_entity` is true or the Escalation Log has any open entry. EQR review is logged as a required step, not performed by the automation.

**Step 10 — Team Review & Sign-Off**
Team resolves Changelog items; partner (and EQR, if triggered) signs. Automation never self-certifies completeness.

## 7. Mandatory Discussion Topics Catalog

**A. Framing**
- A1. Explicit reminder to set aside prior beliefs about management's honesty and integrity
- A2. Susceptibility to fraudulent financial reporting (where/how)
- A3. Susceptibility to misappropriation of assets (where/how)

**B. Rebuttable Presumptions**
- B1. Revenue recognition fraud risk, addressed at the **scheme level** — specific consideration of channel stuffing, bill-and-hold, side letters/undisclosed terms, and multi-element/variable-consideration arrangements relevant to the client's actual revenue streams; if rebutted, rationale must tie to a specific revenue stream, not a general statement
- B2. Management override of controls — addressed as always present, regardless of assessed control environment strength; explicit consideration of manual and **top-side/consolidating entries**

**C. Fraud Triangle Factors** (per identified risk area)
- C1. Incentive/pressure — including compensation tied to results, covenant/debt-compliance pressure, growth expectations, and (if `going_concern_indicator`) going-concern-driven pressure
- C2. Opportunity — control weaknesses, complex or opaque structures, estimate subjectivity
- C3. Rationalization — tone at the top, prior override history, ethical culture signals

**D. Continuity**
- D1. Prior-period fraud or error findings and management's remediation status

**E. Known/Suspected Fraud & Reporting Channels**
- E1. Any known or suspected fraud instances
- E2. Specific inquiry of whether the client's whistleblower/ethics hotline (if one exists) has logged any complaints in the period, and their disposition

**F. IT, Cyber & EUC**
- F1. IT/cyber fraud risk — general access-control and data-manipulation exposure
- F2. Business email compromise / fraudulent wire-transfer exposure, expanded when `cyber_exposure_flag` is set — a now-common real-world vector distinct from generic "IT risk"
- F3. End-user-computing / spreadsheet override risk in significant estimates or consolidation

**G. Unpredictability**
- G1. At least one specific unpredictability element for this engagement

**H. Related Parties & Significant Unusual Transactions**
- H1. Related-party relationships and transactions, including any structured or disclosed in a way that could obscure the related-party nature
- H2. Significant unusual transactions, particularly those occurring near period-end, outside the normal course of business, or with unusual terms

**I. Management Estimates & Accounting Judgments**
- I1. Key estimates susceptible to management bias (goodwill/asset impairment, expected credit loss/allowance, warranty or restructuring reserves, contract assets/costs) and whether a pattern of bias (consistently optimistic or pessimistic) was discussed

**J. Group/Component** (if `complexity_tier = group`)
- J1. Fraud risk factors communicated from group team to component auditors
- J2. Fraud risk factors communicated from component auditors back to group team, with group-team adequacy review recorded (network-firm vs. other-firm tiering)
- J3. Any component with a fraud risk factor requiring group-level response
- J4. Top-side/consolidating-entry risk at the group level specifically (distinct from B2's entity-level manual entries)

**K. First-Year Engagement** (if `engagement_year = first-year`)
- K1. Predecessor auditor communication regarding fraud or fraud risk factors noted in prior periods
- K2. Opening balance fraud risk, including any indication of prior-period manipulation not yet corrected

## 8. Two-Tier Flagging Framework

**Hard gates** (block memo finalization until resolved):
- No discussion date, format, or attendee list on record for any logged session
- Framework or complexity tier unresolved (§6, Step 0)
- B1 or B2 not evidenced at all in any session to date
- Group engagement: any listed component with no Component Fraud Risk Input, or an other-firm component whose adequacy review (Step 3a) hasn't occurred
- Any E1/ad-hoc fraud disclosure not yet routed through Step 6
- `public_interest_entity` or open Escalation entry with no EQR checkpoint logged
- Required `final` session not yet logged once fieldwork is substantially complete

**Graduated flags** (documented, doesn't block finalization):
- A topic evidenced but thin — presumption or factor named without supporting detail
- B1 rebuttal recorded but not tied to a specific revenue stream
- Fraud-triangle coverage skewed to one factor for an identified risk area
- Prior-year finding referenced but remediation status not stated
- Current-year excerpt near-identical to prior-year excerpt for the same topic (boilerplate check, §6 Step 4)
- Component input received but tiered `other-firm` with adequacy review still pending (documented, doesn't block until finalization is actually attempted)

## 9. Guardrails
- Never fabricate discussion content, factors, or attendee statements not present in submitted notes
- Never judge the sufficiency of a presumption rebuttal or the adequacy of a component auditor's work — record and flag for the responsible human role, never conclude
- Never conclude on whether a suspected fraud disclosure is substantiated — route to Escalation Log
- Never draft the actual TCWG/management/regulator fraud communication
- Never assign risk ratings, significance designations, or overall audit strategy linkage — Risk Assessment Memo Generator's job
- Never bypass restricted-access tagging on an Escalation Log entry, even for a "seems minor" disclosure — the access decision belongs to the partner, not the tool
- Never treat prior-year text reuse as current-year evidence, even if the underlying topic is genuinely unchanged — the team must affirmatively confirm it still applies
- Group consolidation never overrides a component's own input; discrepancies are flagged, not reconciled by the tool

## 10. Quality Standards
- Every memo statement traceable to a specific note excerpt, session, and date, or explicitly marked as a gap
- Register rows never left with an inferred fraud-triangle category or assertion — mark "Unclassified — needs team input" if unsupported
- Escalation Log entries timestamped and never deleted; resolution is appended, never overwrites; access list logged alongside each entry
- Handoff exports (§6 Step 7) versioned so the JE Testing Agent and Risk Assessment Memo Generator always consume the latest cumulative state, not a stale planning-only snapshot

## 11. Post-Delivery Feedback Loop
- Team confirms Changelog resolutions before the memo is considered final
- Gaps between checklist prompts and actual note coverage feed back into next engagement's checklist and the per-industry scheme library
- Boilerplate flags feed back into whether the checklist itself needs more client-specific prompts

## 12. Cross-Tool Handoffs
| To | What's exported | Why |
|---|---|---|
| JE Testing & Anomaly Screener | Manual-entry, top-side/consolidating-entry, and period-end-timing risk areas identified in B2/J4 | Scopes where JE testing samples — this tool identifies *where*, JE Testing tests *whether* |
| Risk Assessment Memo Generator | Full Topic-Coverage Record + Fraud Risk Register | Feeds the ISA 315 inherent-risk-factor analysis; this tool never rates significance itself |

See io-spec §5.6–5.7 for exact export schemas.

## 13. Triggers
**Trigger phrases:** "fraud brainstorming," "ISA 240 discussion," "engagement team fraud discussion," "fraud risk session," "brainstorming session" (PCAOB), "document our fraud discussion"
**Explicit non-triggers:** journal entry testing requests → JE Testing & Anomaly Screener; overall risk assessment/risk matrix requests → Risk Assessment Memo Generator; revenue contract review → Revenue Contract Review Agent

## 14. Required Inputs Summary
See io-spec.md §3.

## 15. Output-Format Skill References
- Memo: docx skill
- Risk Register + Escalation Log: xlsx skill
- Discussion Checklist: docx or markdown, per firm preference

## 16. Cowork Execution Notes
- Session notes may arrive as a Cowork meeting transcript — treated identically to typed notes
- Component Fraud Risk Input collected asynchronously; consolidation runs once all components report or the partner overrides with a documented reason
- Ad-hoc session triggers can be raised mid-engagement without waiting for a scheduled checkpoint

## 17. Glossary
- **Fraud triangle**: incentive/pressure, opportunity, rationalization
- **Rebuttable presumption**: a fraud risk the standard requires presumed present unless specifically rebutted with documented rationale
- **Top-side/consolidating entry**: an adjustment made at the group-consolidation level rather than within an individual entity's ledger — a common override vector in group structures
- **Component auditor**: an auditor performing work on a component's financial information for group audit purposes
- **Boilerplate flag**: content recycled from a prior period without evidence of fresh, current-year discussion
- **EQR**: Engagement Quality Reviewer — a second partner-level reviewer required for higher-risk or public-interest engagements
- **Hard gate**: blocks memo finalization until resolved
- **Graduated flag**: documented but doesn't block finalization

## 18. Revision History
| Version | Change |
|---|---|
| 1.0 | Initial single-session, single-framework model |
| 2.0 | Added multi-session lifecycle (planning/interim/final/ad-hoc), dynamic framework detection (ISA/PCAOB/AU-C), management-bias-in-estimates and related-party/significant-unusual-transaction topics, group adequacy review, cyber/BEC specificity, boilerplate detection, cross-tool handoffs, EQR trigger, and first-year overlay |
