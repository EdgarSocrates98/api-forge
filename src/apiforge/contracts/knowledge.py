"""Knowledge source, freshness, drift and impact contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord
from apiforge.contracts.graph import GraphEdge, GraphNode

FreshnessState = Literal[
    "fresh", "stale", "unresolved", "unknown", "verified", "conflicted", "deprecated"
]


class PackApplicability(VersionedContract):
    """Optional version/runtime applicability declared by a Knowledge Pack."""

    versions: tuple[str, ...] = ()
    runtimes: tuple[str, ...] = ()


class PackFreshness(VersionedContract):
    """Optional metadata declared by a Knowledge Pack."""

    window_days: int | None = Field(default=None, ge=0)
    source_hash: str | None = None
    authority: str | None = None
    source_version: str | None = None
    expires_at: str | None = None
    upstream: str | None = None
    last_validated: str | None = None
    applies_to: PackApplicability | None = None


class SourceObservation(VersionedContract):
    """Read-only observation receipt; it does not update a pack."""

    source: str
    observed_at: str
    source_hash: str | None = None
    source_version: str | None = None
    receipt_ref: str
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)


class FreshnessResult(VersionedContract):
    state: FreshnessState
    source: str
    observed_at: str | None = None
    age_days: int | None = Field(default=None, ge=0)
    reason: str
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    next_action: str = "review"


class KnowledgeObservation(VersionedContract):
    """A local or read-only observation about a versioned knowledge pack."""

    domain: str
    pack_version: int = Field(ge=0)
    freshness: FreshnessState
    source_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class KnowledgeDrift(VersionedContract):
    """Drift verdict between a pack declaration and observation receipts.

    ``state`` is the rolled-up FreshnessState; ``conflicts`` names each
    pair of receipts that disagree; ``signals`` records the gate path
    taken; ``unresolved`` keeps every missing input explicit.
    """

    domain: str
    pack_version: int = Field(ge=0)
    state: FreshnessState = "unknown"
    signals: tuple[str, ...] = ()
    conflicts: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    observations: int = Field(default=0, ge=0)
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)


class KnowledgeImpactReport(VersionedContract):
    """source -> pack -> rule -> skill/agent -> eval relation graph.

    Edges derive only from declared data (pack.yaml, source_authority,
    evals, rule catalog, skill/agent manifests); relations that cannot be
    derived are named in ``unresolved``, never fabricated.
    """

    nodes: tuple[GraphNode, ...] = ()
    edges: tuple[GraphEdge, ...] = ()
    totals: dict[str, int] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)


class ExpertisePack(VersionedContract):
    """Validated local domain knowledge that a capability may require."""

    pack_id: str
    domain: str
    pack_version: int = Field(ge=0)
    freshness: FreshnessState = "unknown"
    source_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "unknown"
