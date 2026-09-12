"""
Boilerplate / staleness check — IO-Spec §6.

Compares each topic's current-year supporting_excerpt against the prior
year's excerpt for the *same topic_id*. A similarity above the configured
threshold sets boilerplate_flag = True. This never rejects the content —
genuine no-change situations exist — it only raises a graduated flag
requiring affirmative team confirmation (Skill-Workflow-Spec §9 guardrail:
"Never treat prior-year text reuse as current-year evidence").
"""

from difflib import SequenceMatcher
from typing import Optional

# Char-level ratio on prose, not word-level: audit-memo boilerplate typically
# gets copy-pasted with a light edit (a swapped clause, an updated date), so
# a char-level match tolerates that better than requiring whole words to
# line up. 0.6 catches "same paragraph, lightly reworded"; independently
# drafted text describing the same underlying fact rarely clears it.
DEFAULT_THRESHOLD = 0.6


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    # autojunk=False is required here: SequenceMatcher's default autojunk=True
    # treats any character occurring in more than 1% of a sequence longer than
    # 200 chars as "popular" and excludes it from matching — for ordinary
    # English prose that silently guts the match (a space alone can trip it),
    # collapsing genuinely near-identical paragraphs to a near-zero ratio.
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower(), autojunk=False).ratio()


def apply_boilerplate_check(topic_coverage_records: list, prior_year_excerpts: list,
                             threshold: float = DEFAULT_THRESHOLD) -> list:
    """Mutates and returns topic_coverage_records with boilerplate_flag set
    where applicable. prior_year_excerpts: list of PriorYearExcerpt-like
    objects/dicts with topic_id + text."""
    prior_by_topic = {}
    for p in prior_year_excerpts:
        tid = p.topic_id if hasattr(p, "topic_id") else p["topic_id"]
        text = p.text if hasattr(p, "text") else p["text"]
        prior_by_topic[tid] = text

    for rec in topic_coverage_records:
        prior_text = prior_by_topic.get(rec.topic_id)
        if prior_text and rec.supporting_excerpt:
            score = similarity(rec.supporting_excerpt, prior_text)
            rec.boilerplate_flag = score >= threshold
        else:
            rec.boilerplate_flag = False
    return topic_coverage_records
