---
name: fraud-risk-brainstorming-documenter-io-spec
description: >
  Technical input/output contract for every stage of the Fraud Risk
  Brainstorming Documenter pipeline, including the multi-session lifecycle,
  framework-dynamic behavior, and cross-tool handoff exports. Companion to
  the Skill & Workflow Spec — that document defines the audit methodology;
  this one defines the exact data shapes engineering builds against.
version: 2.0
---

# Fraud Risk Brainstorming Documenter — IO Specification

## 1. Purpose
Defines the exact data contract at every handoff point — including across multiple discussion sessions within one engagement year and across tools in the suite — so checklist generation, note parsing, consolidation, and export can be built and tested independently against a fixed interface.

## 2. Pipeline Data Flow

```
Engagement Metadata (incl. framework, complexity tier, profile flags)
   → [Step 0: Triage] →
Resolved Profile (framework | complexity tier | public-interest | first-year | cyber flag)
   → [Step 1: Checklist Builder, per session_type] →
Discussion Checklist(s)
   → [Step 2: Session(s) — offline] →
Raw Session Notes × N (planning | interim | final | ad-hoc)
   ↓ (group only)
Component Fraud Risk Input × N components
   → [Step 3 / 3a: Consolidation + Adequacy Review, group only] →
Consolidated Notes
   → [Step 4: Cumulative Topic-Coverage Parser + Boilerplate Check] →
Topic-Coverage Record (cumulative across all sessions to date)
   → [Step 5: Memo + Register Drafter] →
Fraud Risk Brainstorming Memo (docx) + Fraud Risk Register (xlsx)
   ↓ (if fraud/suspected fraud disclosed)
Escalation Log entry (restricted access)
   → [Step 7: Cross-Tool Handoff Export] →
JE Testing Agent Scoping Input  |  Risk Assessment Memo Generator Input
   → [Step 9: EQR Checkpoint, conditional] →
   → [Step 8: QA] →
Final Package + Changelog
```

## 3. Input Specification

### 3.1 Engagement Metadata (required)
| Field | Type | Notes |
|---|---|---|
| client_name | text | |
| primary_framework | enum | `ISA` \| `PCAOB` \| `AU-C` — hard gate if unresolved (Skill-Spec §3, §8) |
| industry | text | drives per-industry fraud-scheme library, not a generic prompt |
| fiscal_year_end | date | |
| complexity_tier | enum | `single-entity` \| `group` |
| public_interest_entity | boolean | triggers EQR checkpoint |
| engagement_year | enum | `first-year` \| `recurring` |
| cyber_exposure_flag | boolean | expands F1–F2 into BEC/wire-fraud-specific prompts |
| going_concern_indicator | boolean | adds incentive/pressure prompt under C1 |
| team_members | list[name, role] | drives attendee hard gate |
| components | list[name, materiality_basis, relationship] | `relationship` = `network-firm` \| `other-firm`; required if complexity_tier = group |
| prior_year_findings | text, optional | triggers K-equivalent continuity item (D1) |

### 3.2 Discussion Session record (required, one per session)
| Field | Type | Notes |
|---|---|---|
| session_id | text | unique per session |
| session_type | enum | `planning` \| `interim` \| `final` \| `ad-hoc` |
| trigger_source | text, required if ad-hoc | e.g., "whistleblower disclosure," "management change," "restatement" |
| discussion_date | date | |
| attendees | list[name, role] | |
| raw_notes | text | format-agnostic: plain text, bullets, or transcript (e.g., Cowork capture) |

- `planning` and `final` sessions are required per engagement; `final` must be logged before the memo can be marked complete (hard gate, Skill-Spec §8)
- If a session record is missing date or attendees, the ISA 240.44 / AS 2401.84 hard gate fires immediately and parsing does not proceed for that session until supplied

### 3.3 Prior-Year Fraud Risk Memo (optional)
- Prior period's output from this same tool; used only for the D1 continuity prompt and the boilerplate-similarity check (§6) — never auto-copied into the new memo

### 3.4 Component Fraud Risk Input (required if complexity_tier = group)
| Field | Type | Notes |
|---|---|---|
| component_name | text | must match `components` list in Engagement Metadata |
| component_auditor | text | |
| relationship | enum | `network-firm` \| `other-firm` — inherited from Engagement Metadata, confirmable per component |
| discussion_date | date | |
| topic_coverage_notes | text | component's own raw notes; same format-agnostic rule as §3.2 |
| factors_for_group_attention | text, optional | flagged for J3 |
| adequacy_review_status | enum | `not required` (network-firm) \| `pending` \| `reviewed — sufficient` \| `reviewed — supplementation requested` |

### 3.5 Known/Suspected Fraud Incident Log (optional, in-year)
| Field | Type | Notes |
|---|---|---|
| description | text | |
| date_identified | date | |
| source | enum | `whistleblower` \| `management` \| `audit procedure` \| `other` |
| status | enum | `unresolved` \| `under management review` \| `resolved` |

### 3.6 Whistleblower / Ethics Hotline Log (optional)
| Field | Type | Notes |
|---|---|---|
| complaint_summary | text | |
| date_logged | date | |
| disposition | text | feeds E2 |

## 4. Normalized Internal Schema — Topic-Coverage Record (cumulative)
| Field | Type | Notes |
|---|---|---|
| topic_id | text | e.g., B1, I1, J4 — per skill-spec §7 |
| category | text | Framing / Presumptions / Fraud Triangle / Continuity / Known Fraud / IT-Cyber-EUC / Unpredictability / Related Parties & SUTs / Estimates / Group / First-Year |
| status | enum | `Evidenced` \| `Partially evidenced` \| `Not evidenced` |
| supporting_excerpt | text | verbatim; null if Not evidenced |
| source_session_id | text | which session (§3.2) this was evidenced in |
| component_source | text, optional | which component, group tier only |
| boilerplate_flag | boolean | true if excerpt is a near-verbatim match to the prior year's excerpt for this topic (similarity check, §6) |

## 5. Output Specification

### 5.1 Fraud Risk Brainstorming Memo (docx)
Sections: Header (client, framework, FYE, all sessions logged with dates/attendees) → Framing (A1–A3) → Rebuttable Presumptions (B1–B2, scheme-level detail, rebuttal rationale) → Fraud Triangle Findings by risk area (C1–C3) → Prior-Period Continuity (D1) → Known Fraud & Reporting Channels (E1–E2) → IT/Cyber/EUC (F1–F3) → Unpredictability (G1) → Related Parties & Significant Unusual Transactions (H1–H2) → Management Estimates (I1) → Group/Component Summary (J1–J4, if applicable, incl. adequacy review status) → First-Year Overlay (K1–K2, if applicable) → EQR block (if triggered) → Open Items (Changelog cross-reference) → Sign-off block

### 5.2 Fraud Risk Register (xlsx)
| Column | Notes |
|---|---|
| Risk ID | sequential |
| Risk Description | |
| Fraud Triangle Category | Incentive/Pressure, Opportunity, Rationalization, or Unclassified |
| Financial Statement Assertion | Existence, Completeness, Valuation, Rights & Obligations, Presentation & Disclosure, Cutoff, or Unclassified |
| Account(s) Affected | |
| Source | topic_id / session_id / component that generated this row |
| Planned Response | blank — team completes |

### 5.3 Discussion Checklist (docx or md)
One per `session_type`. Sections: Reminder (A1) → Standing topics (A2–I1, scaled by profile flags per Skill-Spec §5) → Industry-specific scheme prompts (from the maintained per-industry library) → Prior-year carryforward (if D1 triggered) → Group/component block (if applicable) → First-year block (if applicable)

### 5.4 Escalation Log (xlsx, separate file, restricted access)
| Column | Notes |
|---|---|
| Entry ID | |
| Description | from notes or §3.5 |
| Date Identified | |
| Communication Required (per framework, §2 of Skill-Spec) | Yes / Unconfirmed |
| Partner Reviewed | Yes/No — never auto-set to Yes |
| Access List | named individuals only — never defaults to full engagement team |
| Standard-File Clearance | Yes/No — file excluded from standard workpaper set until partner clears it |
| Resolution | appended, never overwrites prior entries |

### 5.5 Changelog
| Field | Notes |
|---|---|
| Item | which hard gate or graduated flag |
| Status | "Pending — awaiting team confirmation" until resolved |
| Resolved By / Date | |

### 5.6 Handoff Export — JE Testing & Anomaly Screener
| Field | Notes |
|---|---|
| risk_area | e.g., "manual entries to revenue near period-end," "top-side consolidating entries" |
| source_topic_id | B2, J4 |
| accounts_implicated | |
| timing_window | if period-end-specific |

### 5.7 Handoff Export — Risk Assessment Memo Generator
- Full Topic-Coverage Record (§4)
- Full Fraud Risk Register (§5.2)
- Consumed as an ISA 315 inherent-risk-factor input; the receiving tool performs its own significance rating — this export carries no rating

## 6. Two-Tier Flagging — Implementation Notes
See skill-spec §8 for the full rule list.
- **Boilerplate check**: current-year `supporting_excerpt` compared against the prior year's excerpt for the same `topic_id` and `client_name`; a similarity match above the firm's configured threshold sets `boilerplate_flag = true` and raises a graduated flag — never auto-rejects the content, since genuine no-change situations exist, but always requires affirmative team confirmation
- Hard gates prevent the memo status field from being set to "Final" — a draft docx still generates, watermarked "DRAFT — Open Items Pending"
- Graduated flags never block finalization, only populate the Changelog

## 7. Formatting & Audit Trail Standards
- Every memo paragraph carries an inline footnote to its `source_session_id` and excerpt location
- Register and Escalation Log rows are never deleted, only status-updated
- Escalation Log entries and any memo section drawing on them are tagged with the Access List from §5.4 — general engagement team distribution is blocked until Standard-File Clearance = Yes
- File naming: `[Client]_FraudBrainstorming_[FYE]_[session_type or "Full"]_[v#].docx / .xlsx`

## 8. Pre-Delivery Checklist
- [ ] All hard gates resolved or explicitly overridden with partner sign-off on record
- [ ] `planning` and `final` sessions both logged
- [ ] Every register row has a non-null Fraud Triangle Category, Assertion, or "Unclassified"
- [ ] Group tier: every listed component has input, and every `other-firm` component has a completed adequacy review
- [ ] Any Escalation Log entry has Communication Required populated and an Access List set
- [ ] EQR checkpoint logged if `public_interest_entity` or any open Escalation entry
- [ ] Handoff exports (§5.6–5.7) generated and versioned to the latest cumulative state
- [ ] Changelog matches every flag raised in Steps 4–6

## 9. Changelog Table Template
| Item | Status | Resolved By / Date |
|---|---|---|
| e.g., "B2 (management override) not evidenced in any session to date" | Pending — awaiting team confirmation | |

## 10. Framework Quick-Reference
| Topic | ISA 240 | PCAOB AS 2401 | AU-C 240 |
|---|---|---|---|
| Discussion terminology | "discussion among the engagement team" | "brainstorming session" | "discussion among the engagement team" |
| Revenue recognition presumption | 240.26–27 | AS 2401.54 | 240.27 |
| Management override presumption | 240.31–33 | AS 2401.65 | 240.31 |
| Documentation requirement | 240.44 | AS 2401.84 | 240.44 |
Full paragraph-level detail lives in the per-framework reference files (Skill-Spec §3), not duplicated here.

## 11. Revision History
| Version | Change |
|---|---|
| 1.0 | Single-session, single-framework schema |
| 2.0 | Multi-session lifecycle fields, framework field + quick-reference, component adequacy review fields, boilerplate-check mechanics, cross-tool handoff export schemas (§5.6–5.7), Escalation Log access-control fields, first-year and cyber-exposure profile flags |
