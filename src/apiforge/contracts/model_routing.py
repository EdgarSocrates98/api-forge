"""Model routing and adaptive retrieval contracts (step11 §33-§39)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.agentic_governance import (
    ControlPlaneMode,
    DecisionRisk,
    GovernorComplexity,
)
from apiforge.contracts.base import VersionedContract

RoutingKind = Literal["capability", "agent", "model"]
ModelAvailability = Literal["available", "degraded", "unavailable", "unknown"]
ModelTaskClass = Literal["analysis", "generation", "verification", "extraction", "routing"]
RetrievalLevel = Literal["L0", "L1", "L2", "L3", "L4"]
RewriteGate = Literal["allowed", "deterministic_succeeded", "budget_blocked", "profile_blocked"]


class ModelRouteInputs(VersionedContract):
    """§33 declared inputs for a model routing decision.

    Every field is a declared signal: values the caller did not supply land
    in ``unresolved`` — nothing is inferred from task text.
    """

    schema: Literal["apiforge/model-route-inputs/v1"] = "apiforge/model-route-inputs/v1"  # type: ignore[assignment]
    task_complexity: GovernorComplexity | None = None
    task_class: ModelTaskClass | None = None
    risk: DecisionRisk | None = None
    reasoning_needs: Literal["none", "light", "deep"] | None = None
    context_size: int | None = Field(default=None, ge=0)
    needs_tool_support: bool | None = None
    needs_structured_output: bool | None = None
    max_latency_ms: int | None = Field(default=None, ge=0)
    max_cost: float | None = Field(default=None, ge=0)
    budget_remaining: dict[str, int | float | None] = Field(default_factory=dict)
    allow_challenger: bool = False


class ModelCandidate(VersionedContract):
    """One provider/model descriptor the router may rank."""

    schema: Literal["apiforge/model-candidate/v1"] = "apiforge/model-candidate/v1"  # type: ignore[assignment]
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    tool_support: bool = False
    structured_output: bool = False
    context_window: int = Field(default=0, ge=0)
    reasoning_tier: Literal["none", "light", "deep"] = "none"
    availability: ModelAvailability = "unknown"
    cost_per_1k: float | None = Field(default=None, ge=0)
    latency_p50_ms: int | None = Field(default=None, ge=0)
    role: Literal["champion", "challenger", "fallback"] = "fallback"


class ModelEvaluation(VersionedContract):
    """§34 one observed evaluation feeding a ModelScorecard."""

    schema: Literal["apiforge/model-evaluation/v1"] = "apiforge/model-evaluation/v1"  # type: ignore[assignment]
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    task_class: ModelTaskClass
    quality: float | None = Field(default=None, ge=0, le=1)
    tool_selection_accuracy: float | None = Field(default=None, ge=0, le=1)
    evidence_correctness: float | None = Field(default=None, ge=0, le=1)
    structured_output_reliability: float | None = Field(default=None, ge=0, le=1)
    latency_ms: float | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
    failed: bool = False
    recorded_at: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()


class ModelScorecard(VersionedContract):
    """§34 per provider/model quality history, segmented by task class."""

    schema: Literal["apiforge/model-scorecard/v1"] = "apiforge/model-scorecard/v1"  # type: ignore[assignment]
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    task_class: ModelTaskClass
    evaluation_count: int = Field(default=0, ge=0)
    quality: float | None = Field(default=None, ge=0, le=1)
    tool_selection_accuracy: float | None = Field(default=None, ge=0, le=1)
    evidence_correctness: float | None = Field(default=None, ge=0, le=1)
    structured_output_reliability: float | None = Field(default=None, ge=0, le=1)
    latency_p50_ms: float | None = Field(default=None, ge=0)
    cost_mean: float | None = Field(default=None, ge=0)
    failure_rate: float | None = Field(default=None, ge=0, le=1)
    freshness_state: Literal[
        "fresh", "cold", "warming", "mature", "stale", "degraded", "unresolved", "unknown"
    ] = "unknown"
    observed_at: str | None = None
    unresolved: tuple[str, ...] = ()


class RankedModel(VersionedContract):
    """One ranked entry inside a ModelRouteDecision."""

    schema: Literal["apiforge/ranked-model/v1"] = "apiforge/ranked-model/v1"  # type: ignore[assignment]
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    eligible: bool
    score: float | None = Field(default=None, ge=0, le=1)
    reasons: tuple[str, ...] = ()


class ModelRouteDecision(VersionedContract):
    """§33 the routing answer; ``routing_kind`` keeps the planes separate."""

    schema: Literal["apiforge/model-route-decision/v1"] = "apiforge/model-route-decision/v1"  # type: ignore[assignment]
    routing_kind: Literal["model"] = "model"
    selected: str | None = None
    ranked: tuple[RankedModel, ...] = ()
    code: str | None = None
    reason: str = ""
    unresolved: tuple[str, ...] = ()


class ModelRouteShadowReceipt(VersionedContract):
    """§33/§29 run-scoped proof the candidate router ran without governing.

    ``route_model_shadow`` also appends the §29 ``ShadowRecord`` to the
    control-plane ledger; this receipt binds that observation to the run:
    declared inputs, the candidate decision, the legacy decision that kept
    governing and the control-plane verdict. ``invalid_inputs`` records
    ``model_route_*`` spec values that failed validation — rejected, never
    guessed. ``code`` carries the router refusal when no candidate survived
    or the policy could not be loaded.
    """

    schema: Literal["apiforge/model-route-shadow-receipt/v1"] = (
        "apiforge/model-route-shadow-receipt/v1"  # type: ignore[assignment]
    )
    route: Literal["model_routing"] = "model_routing"
    mode: ControlPlaneMode | None = None
    governing: Literal["legacy", "candidate", "none"] | None = None
    inputs: ModelRouteInputs
    legacy_decision: dict[str, object] = Field(default_factory=dict)
    candidate: ModelRouteDecision | None = None
    control: dict[str, object] | None = None
    code: str | None = None
    invalid_inputs: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    recorded_at: str = Field(min_length=1)


class RetrievalStep(VersionedContract):
    """One level attempted inside an adaptive retrieval ladder.

    ``top_score`` is the level's effective top score after its declared
    weighting. ``raw_top_score`` preserves the source score for diagnostics.
    """

    schema: Literal["apiforge/retrieval-step/v1"] = "apiforge/retrieval-step/v1"  # type: ignore[assignment]
    level: RetrievalLevel
    hits: int = Field(ge=0)
    top_score: float | None = Field(default=None, ge=0)
    raw_top_score: float | None = Field(default=None, ge=0)
    escalated: bool = False
    reason: str = ""


class AdaptiveRetrievalResult(VersionedContract):
    """§36 the ladder outcome: the level that sufficed, with the trace."""

    schema: Literal["apiforge/adaptive-retrieval-result/v1"] = (
        "apiforge/adaptive-retrieval-result/v1"  # type: ignore[assignment]
    )
    query: str = Field(min_length=1)
    level_used: RetrievalLevel
    steps: tuple[RetrievalStep, ...] = ()
    hits: tuple[str, ...] = ()
    semantic_available: bool = False
    provenance: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()


class QueryRewrite(VersionedContract):
    """§39 original vs rewritten query — gated, never silent."""

    schema: Literal["apiforge/query-rewrite/v1"] = "apiforge/query-rewrite/v1"  # type: ignore[assignment]
    original: str = Field(min_length=1)
    rewritten: str | None = None
    gate: RewriteGate
    reason: str = ""


class RetrievalComparison(VersionedContract):
    """§38 per-strategy metrics over a gold corpus."""

    schema: Literal["apiforge/retrieval-comparison/v1"] = "apiforge/retrieval-comparison/v1"  # type: ignore[assignment]
    strategy: Literal["lexical", "graph", "semantic", "hybrid"]
    recall: float | None = Field(default=None, ge=0, le=1)
    precision: float | None = Field(default=None, ge=0, le=1)
    latency_ms: float | None = Field(default=None, ge=0)
    tokens: float | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
    unresolved: tuple[str, ...] = ()


__all__ = [
    "AdaptiveRetrievalResult",
    "ModelAvailability",
    "ModelCandidate",
    "ModelEvaluation",
    "ModelRouteDecision",
    "ModelRouteInputs",
    "ModelRouteShadowReceipt",
    "ModelScorecard",
    "ModelTaskClass",
    "QueryRewrite",
    "RankedModel",
    "RetrievalComparison",
    "RetrievalLevel",
    "RetrievalStep",
    "RewriteGate",
    "RoutingKind",
]
