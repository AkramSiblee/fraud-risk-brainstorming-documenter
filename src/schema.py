"""
Core data schemas — mirrors IO-Spec.md §3 (inputs), §4 (topic-coverage record),
§5 (outputs). Plain dataclasses + dict (de)serialization, no external
dependency, so this runs anywhere Python 3.9+ runs.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


def _load(cls, d: dict):
    kwargs = {k: d[k] for k in cls.__dataclass_fields__.keys() if k in d}
    return cls(**kwargs)


@dataclass
class TeamMember:
    name: str
    role: str


@dataclass
class Component:
    name: str
    materiality_basis: str
    relationship: str  # "network-firm" | "other-firm"


@dataclass
class EngagementMetadata:
    client_name: str
    primary_framework: str  # "ISA" | "PCAOB" | "AU-C"
    industry: str
    fiscal_year_end: str
    complexity_tier: str  # "single-entity" | "group"
    public_interest_entity: bool
    engagement_year: str  # "first-year" | "recurring"
    cyber_exposure_flag: bool
    going_concern_indicator: bool
    team_members: list = field(default_factory=list)   # list[TeamMember]
    components: list = field(default_factory=list)      # list[Component]
    prior_year_findings: Optional[str] = None


@dataclass
class DiscussionSession:
    session_id: str
    session_type: str  # "planning" | "interim" | "final" | "ad-hoc"
    discussion_date: str
    attendees: list  # list[str] "Name (Role)"
    raw_notes: str
    trigger_source: Optional[str] = None
    source_file: Optional[str] = None


@dataclass
class ComponentFraudRiskInput:
    component_name: str
    component_auditor: str
    relationship: str
    discussion_date: Optional[str]
    topic_coverage_notes: Optional[str]
    factors_for_group_attention: Optional[str] = None
    adequacy_review_status: str = "not required"  # enum, see IO-Spec §3.4
    received: bool = True


@dataclass
class KnownSuspectedFraudIncident:
    entry_id: str
    description: str
    date_identified: str
    source: str  # "whistleblower" | "management" | "audit procedure" | "other"
    status: str  # "unresolved" | "under management review" | "resolved"


@dataclass
class WhistleblowerHotlineEntry:
    date_logged: str
    complaint_summary: str
    disposition: str


@dataclass
class PriorYearExcerpt:
    topic_id: str
    text: str


@dataclass
class IngestedPackage:
    metadata: EngagementMetadata
    sessions: list  # list[DiscussionSession]
    component_inputs: list  # list[ComponentFraudRiskInput]
    incidents: list  # list[KnownSuspectedFraudIncident]
    hotline_entries: list  # list[WhistleblowerHotlineEntry]
    prior_year_excerpts: list  # list[PriorYearExcerpt]

    def to_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(_serialize(self), f, indent=2, default=str, ensure_ascii=False)

    @staticmethod
    def from_json(path: str) -> "IngestedPackage":
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        md_dict = dict(d["metadata"])
        md_dict["team_members"] = [_load(TeamMember, tm) for tm in md_dict.get("team_members", [])]
        md_dict["components"] = [_load(Component, c) for c in md_dict.get("components", [])]
        metadata = _load(EngagementMetadata, md_dict)
        return IngestedPackage(
            metadata=metadata,
            sessions=[_load(DiscussionSession, s) for s in d["sessions"]],
            component_inputs=[_load(ComponentFraudRiskInput, c) for c in d["component_inputs"]],
            incidents=[_load(KnownSuspectedFraudIncident, i) for i in d["incidents"]],
            hotline_entries=[_load(WhistleblowerHotlineEntry, h) for h in d["hotline_entries"]],
            prior_year_excerpts=[_load(PriorYearExcerpt, p) for p in d["prior_year_excerpts"]],
        )


def _serialize(obj):
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    if isinstance(obj, list):
        return [_serialize(x) for x in obj]
    return obj


@dataclass
class TopicCoverageRecord:
    topic_id: str
    category: str
    status: str  # "Evidenced" | "Partially evidenced" | "Not evidenced"
    supporting_excerpt: Optional[str]
    source_session_id: Optional[str]
    component_source: Optional[str] = None
    boilerplate_flag: bool = False
    # Free-form short tags a human or Claude Code can attach during the
    # topic-coverage step, for judgment calls the deterministic flag engine
    # can't make on its own (e.g. "rebuttal_not_stream_specific" on B1,
    # "remediation_status_not_stated" on D1). See flag_engine.py for the
    # tags it currently recognizes.
    qualifier_flags: list = field(default_factory=list)


@dataclass
class FraudRiskRegisterRow:
    risk_id: str
    risk_description: str
    fraud_triangle_category: str  # Incentive/Pressure | Opportunity | Rationalization | Unclassified
    assertion: str  # Existence | Completeness | Valuation | Rights & Obligations | Presentation & Disclosure | Cutoff | Unclassified
    accounts_affected: str
    source: str  # topic_id / session_id / component
    planned_response: str = ""


@dataclass
class EscalationLogEntry:
    entry_id: str
    description: str
    date_identified: str
    communication_required: str  # "Yes" | "Unconfirmed"
    partner_reviewed: str = "No"
    access_list: str = ""
    standard_file_clearance: str = "No"
    resolution: str = ""


@dataclass
class ChangelogItem:
    item: str
    status: str = "Pending — awaiting team confirmation"
    resolved_by_date: str = ""


def load_json_list(path: str, cls):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [_load(cls, d) for d in data]


def dump_json_list(items: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([_serialize(i) for i in items], f, indent=2, default=str, ensure_ascii=False)
