"""
Mandatory Discussion Topics Catalog — mirrors Skill-Workflow-Spec.md §7 exactly.
This is the single source of truth for topic_ids used across ingestion,
topic-coverage parsing, flagging, and export. If the spec changes, change it
here first — everything else reads from this module.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Topic:
    topic_id: str
    category: str
    description: str
    # applies_if: None means always applies; otherwise a profile flag name that
    # must be truthy/equal to a given value for this topic to be in scope.
    applies_if: Optional[str] = None
    applies_value: Optional[object] = None


CATALOG = [
    # A. Framing
    Topic("A1", "Framing", "Explicit reminder to set aside prior beliefs about management's honesty and integrity"),
    Topic("A2", "Framing", "Susceptibility to fraudulent financial reporting (where/how)"),
    Topic("A3", "Framing", "Susceptibility to misappropriation of assets (where/how)"),

    # B. Rebuttable Presumptions
    Topic("B1", "Presumptions",
          "Revenue recognition fraud risk, addressed at the scheme level (channel stuffing, bill-and-hold, "
          "side letters, multi-element/variable-consideration arrangements). If rebutted, rationale must tie "
          "to a specific revenue stream."),
    Topic("B2", "Presumptions",
          "Management override of controls, addressed as always present regardless of assessed control "
          "environment strength; explicit consideration of manual and top-side/consolidating entries"),

    # C. Fraud Triangle (per identified risk area)
    Topic("C1", "Fraud Triangle", "Incentive/pressure factors"),
    Topic("C2", "Fraud Triangle", "Opportunity factors"),
    Topic("C3", "Fraud Triangle", "Rationalization factors"),

    # D. Continuity — only meaningful where a prior-year memo from this firm
    # could exist. On a first-year engagement there is no such memo (see K1/K2
    # for the equivalent first-year concept: predecessor communication and
    # opening-balance risk, which cover this territory instead).
    Topic("D1", "Continuity", "Prior-period fraud or error findings and management's remediation status",
          applies_if="engagement_year", applies_value="recurring"),

    # E. Known/Suspected Fraud & Reporting Channels
    Topic("E1", "Known Fraud", "Any known or suspected fraud instances"),
    Topic("E2", "Known Fraud",
          "Specific inquiry into whether the client's whistleblower/ethics hotline has logged complaints, "
          "and their disposition"),

    # F. IT, Cyber & EUC
    Topic("F1", "IT-Cyber-EUC", "IT/cyber fraud risk — general access-control and data-manipulation exposure"),
    Topic("F2", "IT-Cyber-EUC",
          "Business email compromise / fraudulent wire-transfer exposure (expanded when cyber_exposure_flag "
          "is set)"),
    Topic("F3", "IT-Cyber-EUC", "End-user-computing / spreadsheet override risk in significant estimates or consolidation"),

    # G. Unpredictability
    Topic("G1", "Unpredictability", "At least one specific unpredictability element for this engagement"),

    # H. Related Parties & Significant Unusual Transactions
    Topic("H1", "Related Parties & SUTs",
          "Related-party relationships and transactions, including any structured to obscure the "
          "related-party nature"),
    Topic("H2", "Related Parties & SUTs",
          "Significant unusual transactions, particularly near period-end, outside the normal course of "
          "business, or with unusual terms"),

    # I. Management Estimates
    Topic("I1", "Estimates",
          "Key estimates susceptible to management bias (impairment, ECL/allowance, reserves, contract "
          "assets/costs) and whether a pattern of bias was discussed"),

    # J. Group/Component (only if complexity_tier == group)
    Topic("J1", "Group", "Fraud risk factors communicated from group team to component auditors",
          applies_if="complexity_tier", applies_value="group"),
    Topic("J2", "Group",
          "Fraud risk factors communicated from component auditors back to group team, with group-team "
          "adequacy review recorded",
          applies_if="complexity_tier", applies_value="group"),
    Topic("J3", "Group", "Any component with a fraud risk factor requiring group-level response",
          applies_if="complexity_tier", applies_value="group"),
    Topic("J4", "Group", "Top-side/consolidating-entry risk at the group level specifically",
          applies_if="complexity_tier", applies_value="group"),

    # K. First-Year Engagement (only if engagement_year == first-year)
    Topic("K1", "First-Year",
          "Predecessor auditor communication regarding fraud or fraud risk factors noted in prior periods",
          applies_if="engagement_year", applies_value="first-year"),
    Topic("K2", "First-Year",
          "Opening balance fraud risk, including any indication of prior-period manipulation not yet corrected",
          applies_if="engagement_year", applies_value="first-year"),
]

CATALOG_BY_ID = {t.topic_id: t for t in CATALOG}

VALID_STATUSES = ("Evidenced", "Partially evidenced", "Not evidenced")


def topics_in_scope(profile: dict) -> list:
    """Return the Topic objects that apply given an engagement profile dict
    (must contain complexity_tier and engagement_year keys)."""
    in_scope = []
    for t in CATALOG:
        if t.applies_if is None:
            in_scope.append(t)
        elif profile.get(t.applies_if) == t.applies_value:
            in_scope.append(t)
    return in_scope
