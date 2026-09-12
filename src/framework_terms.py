"""
Framework-specific terminology and citations — Skill-Workflow-Spec §2/§3,
IO-Spec §10. Kept as pure data (not scattered string literals) so a fourth
framework is one dict entry, not a hunt through export scripts.
"""

FRAMEWORK_TERMS = {
    "ISA": {
        "discussion_label": "Discussion Among the Engagement Team",
        "skepticism_citation": "ISA 240.15",
        "b1_citation": "ISA 240.26\u201327",
        "b2_citation": "ISA 240.31\u201333",
        "documentation_citation": "ISA 240.44",
        "partner_participation_expected": False,
    },
    "PCAOB": {
        "discussion_label": "Brainstorming Session",
        "skepticism_citation": "AS 2401.05, .52",
        "b1_citation": "AS 2401.54",
        "b2_citation": "AS 2401.65",
        "documentation_citation": "AS 2401.84",
        "partner_participation_expected": True,
    },
    "AU-C": {
        "discussion_label": "Discussion Among the Engagement Team",
        "skepticism_citation": "AU-C 240.15",
        "b1_citation": "AU-C 240.27",
        "b2_citation": "AU-C 240.31",
        "documentation_citation": "AU-C 240.44",
        "partner_participation_expected": False,
    },
}

DEFAULT = FRAMEWORK_TERMS["ISA"]


def terms_for(framework: str) -> dict:
    return FRAMEWORK_TERMS.get(framework, DEFAULT)
