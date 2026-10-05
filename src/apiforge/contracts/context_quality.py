"""Context-quality contracts: measured capsule quality, sufficiency and role policy v2.

Every metric carries an explicit basis: ``observed`` (derived from recorded
ledger/use rows), ``estimated`` (derived with a declared approximation) or
``unresolved`` (the input needed to compute it was never recorded). The engine
never invents a value for an unresolved metric.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.context import RefKind, RefOrigin
from apiforge.contracts.selective import RoleKind

MetricBasis = Literal["observed", "estimated", "unresolved"]

ContextMetricKind = Literal[
    "context_precision",
    "context_recall",
    "evidence_recall",
    "context_density",
    "duplicate_context_ratio",
    "irrelevant_context_ratio",
    "stale_context_ratio",
    "context_expansion_rate",
    "context_reuse_rate",
    "cache_hit_rate",
    "role_context_efficiency",
    "selected_evidence_utilization",
    "evidence_per_token",
    "useful_facts_per_1k_tokens",
]

METRIC_KINDS: tuple[ContextMetricKind, ...] = (
    "context_precision",
    "context_recall",
    "evidence_recall",
    "context_density",
    "duplicate_context_ratio",
    "irrelevant_context_ratio",
    "stale_context_ratio",
    "context_expansion_rate",
    "context_reuse_rate",
    "cache_hit_rate",
    "role_context_efficiency",
    "selected_evidence_utilization",
    "evidence_per_token",
    "useful_facts_per_1k_tokens",
)

UseAction = Literal["loaded", "assigned", "expanded", "cited", "artifact"]
VisibilityLevel = Literal["none", "summary", "full"]
SufficiencyGate = Literal["strict", "evidence", "permissive"]

#: Actions that mean the ref content actually reached a consumer.
CONSUMED_ACTIONS: tuple[UseAction, ...] = ("expanded", "cited", "artifact")

#: Ref kinds treated as evidence supporting a claim (``code`` is the artifact).
EVIDENCE_KINDS: tuple[RefKind, ...] = ("contract", "schema", "policy", "knowledge", "test")


class ContextUseRecord(VersionedContract):
    """One recorded interaction between a consumer and a ctx:// ref.

    Produced from the run ledger (capsule admission, role assignment,
    ``context expand``) or supplied by an eval fixture; ``tokens`` is only
    ``observed`` when it came from a measured transcript field.
    """

    use_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    ref_uri: str = Field(min_length=1)
    action: UseAction
    role: str | None = None
    bytes: int = Field(default=0, ge=0)
    tokens: int | None = Field(default=None, ge=0)
    tokens_basis: MetricBasis = "observed"


class ContextQualityMetric(VersionedContract):
    """One metric of a capsule/run; ``value`` is null when the basis is unresolved."""

    name: ContextMetricKind
    value: float | None = Field(default=None, ge=0.0)
    unit: str = "ratio"
    basis: MetricBasis = "observed"
    detail: str = ""

    @model_validator(mode="after")
    def value_matches_basis(self) -> ContextQualityMetric:
        if self.basis == "unresolved" and self.value is not None:
            raise ValueError("unresolved metrics carry no value")
        if self.basis != "unresolved" and self.value is None:
            raise ValueError("observed/estimated metrics require a value")
        return self


class RoleContextQuality(VersionedContract):
    """Per-role rollup inside a quality report."""

    role: str
    refs_assigned: int = Field(default=0, ge=0)
    refs_used: int = Field(default=0, ge=0)
    bytes_assigned: int = Field(default=0, ge=0)
    bytes_used: int = Field(default=0, ge=0)
    efficiency: float | None = Field(default=None, ge=0.0, le=1.0)


class ContextQualityReport(VersionedContract):
    """Measured quality of one capsule/run selection; all metric kinds emitted."""

    schema: Literal["apiforge/context-quality/v1"] = "apiforge/context-quality/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    capsule_id: str | None = None
    refs_total: int = Field(default=0, ge=0)
    refs_used: int = Field(default=0, ge=0)
    uses_total: int = Field(default=0, ge=0)
    metrics: tuple[ContextQualityMetric, ...] = ()
    roles: tuple[RoleContextQuality, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved"] = "ready"

    @model_validator(mode="after")
    def metrics_cover_catalog(self) -> ContextQualityReport:
        names = [metric.name for metric in self.metrics]
        if len(set(names)) != len(names):
            raise ValueError("duplicate metric names in report")
        missing = [name for name in METRIC_KINDS if name not in names]
        if missing:
            raise ValueError(f"report must emit every metric kind; missing {missing}")
        return self


class ContextSufficiencyResult(VersionedContract):
    """Minimum-sufficient-context decision: what prunes without quality loss."""

    schema: Literal["apiforge/context-sufficiency/v1"] = "apiforge/context-sufficiency/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    capsule_id: str | None = None
    gate: SufficiencyGate = "strict"
    kept_refs: tuple[str, ...] = ()
    pruned_refs: tuple[str, ...] = ()
    pruned_bytes: int = Field(default=0, ge=0)
    metrics_before: tuple[ContextQualityMetric, ...] = ()
    metrics_after: tuple[ContextQualityMetric, ...] = ()
    sufficient: bool = False
    unresolved: tuple[str, ...] = ()


class RoleContextPolicy(VersionedContract):
    """RoleContext v2 policy row (prompt §7): declared per role in
    ``rules/role_context.yaml`` under ``policies:``; absent fields keep the
    permissive v1 defaults so existing plans are unchanged.

    ``required_kinds`` are delivered first inside the role's budget; a kind
    that *was* in the capsule but did not fit is a violation
    (``AF-ROLE-CONTEXT-REQUIRED``), while a kind absent from the world is not —
    requirements never conjure evidence. ``minimum_origin_rank`` is trust
    derived deterministically from the ref's declared ``origin`` —
    ``filesystem`` < ``knowledge`` < ``code`` < ``graph`` < ``contract`` —
    never an asserted model trust score.
    """

    role: RoleKind
    required_kinds: tuple[RefKind, ...] = ()
    denied_kinds: tuple[RefKind, ...] = ()
    memory_visibility: VisibilityLevel = "full"
    knowledge_visibility: VisibilityLevel = "full"
    artifact_visibility: VisibilityLevel = "full"
    tool_visibility: tuple[str, ...] = ()
    minimum_origin_rank: RefOrigin | None = None
    max_context_bytes: int | None = Field(default=None, ge=0)
    max_context_tokens: int | None = Field(default=None, ge=0)
    required_evidence: bool = False

    @model_validator(mode="after")
    def kinds_are_disjoint(self) -> RoleContextPolicy:
        conflict = set(self.required_kinds) & set(self.denied_kinds)
        if conflict:
            raise ValueError(f"required_kinds and denied_kinds overlap: {sorted(conflict)}")
        return self


class RoleContextTelemetry(VersionedContract):
    """Per-role measured context counters (prompt §7): loaded, expanded,
    cited, tokens, evidence, cache hits, duplicates and the unused estimate."""

    schema: Literal["apiforge/role-context-telemetry/v1"] = "apiforge/role-context-telemetry/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    role: str = Field(min_length=1)
    capability: str = ""
    refs_assigned: int = Field(default=0, ge=0)
    refs_expanded: int = Field(default=0, ge=0)
    refs_cited: int = Field(default=0, ge=0)
    context_bytes: int = Field(default=0, ge=0)
    tokens: int | None = Field(default=None, ge=0)
    tokens_basis: MetricBasis = "observed"
    evidence_refs: int = Field(default=0, ge=0)
    cache_hits: int = Field(default=0, ge=0)
    duplicates: int = Field(default=0, ge=0)
    unused_refs: int = Field(default=0, ge=0)


__all__ = [
    "CONSUMED_ACTIONS",
    "EVIDENCE_KINDS",
    "METRIC_KINDS",
    "ContextMetricKind",
    "ContextQualityMetric",
    "ContextQualityReport",
    "ContextSufficiencyResult",
    "ContextUseRecord",
    "MetricBasis",
    "RoleContextPolicy",
    "RoleContextQuality",
    "RoleContextTelemetry",
    "SufficiencyGate",
    "UseAction",
    "VisibilityLevel",
]
