"""Versioned contracts for the eval plane (§23–§25): trace grading, the
live-model layer, the quality/cost frontier and the adversarial/memory
eval reports.

Every axis keeps the platform invariant — unresolved states are explicit
and carry the reason; provider-derived numbers are never inferred.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue

TraceVerdict = Literal["pass", "review", "fail", "unresolved"]
ProviderTier = Literal["deferred_external", "declared", "observed"]
DefenseVerdict = Literal["contained", "refused", "escaped"]


class TraceGradeDimension(VersionedContract):
    """One rubric dimension scored over one trace."""

    schema: Literal["apiforge/trace-grade-dimension/v1"] = "apiforge/trace-grade-dimension/v1"  # type: ignore[assignment]
    dimension: str = Field(min_length=1)
    weight: float = Field(ge=0, le=1)
    score: float | None = Field(default=None, ge=0, le=1)
    state: Literal["observed", "unresolved"] = "observed"
    signals_found: tuple[str, ...] = ()
    signals_missing: tuple[str, ...] = ()
    detail: str = ""

    @model_validator(mode="after")
    def _unresolved_carries_reason(self) -> TraceGradeDimension:
        if self.state == "unresolved":
            if self.score is not None:
                raise ValueError("unresolved dimension cannot carry a score")
            if not self.detail:
                raise ValueError("unresolved dimension requires detail")
        return self


class TraceGrade(VersionedContract):
    """The graded result for one trace under one rubric."""

    schema: Literal["apiforge/trace-grade/v1"] = "apiforge/trace-grade/v1"  # type: ignore[assignment]
    trace_id: str = Field(min_length=1)
    rubric_id: str = Field(min_length=1)
    dimensions: tuple[TraceGradeDimension, ...] = ()
    score: float | None = Field(default=None, ge=0, le=1)
    verdict: TraceVerdict = "unresolved"
    evidence_refs: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class TraceGradingReport(VersionedContract):
    """§23 trace grading over a set of recorded traces."""

    schema: Literal["apiforge/trace-grading-report/v1"] = "apiforge/trace-grading-report/v1"  # type: ignore[assignment]
    rubric_id: str = Field(min_length=1)
    grades: tuple[TraceGrade, ...] = ()
    unresolved: tuple[str, ...] = ()


class LiveEvalLayer(VersionedContract):
    """§23 the declared periodic eval layer: profiles, axes, tiers."""

    schema: Literal["apiforge/live-eval-layer/v1"] = "apiforge/live-eval-layer/v1"  # type: ignore[assignment]
    profiles: tuple[str, ...] = ("economy", "balanced", "deep")
    metrics: tuple[str, ...] = (
        "correctness",
        "evidence_quality",
        "tool_selection",
        "routing_accuracy",
        "handoff_quality",
        "security_behavior",
        "latency",
        "tokens",
        "cost",
    )
    deterministic_evals: tuple[str, ...] = ()
    corpus_refs: tuple[str, ...] = ()
    provider_tier: ProviderTier = "deferred_external"


class LiveEvalReport(VersionedContract):
    """§23 one run of the layer: deterministic tier observed, provider
    tier declared — unresolved unless an adapter actually ran."""

    schema: Literal["apiforge/live-eval-report/v1"] = "apiforge/live-eval-report/v1"  # type: ignore[assignment]
    layer: LiveEvalLayer
    deterministic: dict[str, JsonValue] = Field(default_factory=dict)
    provider_status: ProviderTier = "deferred_external"
    provider_results: dict[str, JsonValue] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _provider_results_need_observation(self) -> LiveEvalReport:
        if self.provider_status != "observed" and self.provider_results:
            raise ValueError("provider_results require provider_status=observed")
        if self.provider_status == "deferred_external" and not self.unresolved:
            raise ValueError("deferred_external provider tier must name the reason in unresolved")
        return self


class FrontierPoint(VersionedContract):
    """§23 quality × cost × latency for one profile. `cost` stays None +
    unresolved without provider-accounted data — never inferred."""

    schema: Literal["apiforge/frontier-point/v1"] = "apiforge/frontier-point/v1"  # type: ignore[assignment]
    profile: str = Field(min_length=1)
    quality: float | None = Field(default=None, ge=0, le=1)
    latency_ms: float | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
    cost_state: Literal["observed", "unresolved"] = "unresolved"
    pareto: bool = False
    detail: str = ""

    @model_validator(mode="after")
    def _cost_consistency(self) -> FrontierPoint:
        if self.cost_state == "unresolved" and self.cost is not None:
            raise ValueError("unresolved cost cannot carry a value")
        if self.cost_state == "observed" and self.cost is None:
            raise ValueError("observed cost requires a value")
        return self


class QualityFrontier(VersionedContract):
    """§23 the frontier report across declared profiles."""

    schema: Literal["apiforge/quality-frontier/v1"] = "apiforge/quality-frontier/v1"  # type: ignore[assignment]
    points: tuple[FrontierPoint, ...] = ()
    pareto_profiles: tuple[str, ...] = ()
    source: str = ""
    unresolved: tuple[str, ...] = ()


class AdversarialCaseResult(VersionedContract):
    """§25 one synthesized attack against one defense surface."""

    schema: Literal["apiforge/adversarial-case-result/v1"] = "apiforge/adversarial-case-result/v1"  # type: ignore[assignment]
    case_id: str = Field(min_length=1)
    attack_class: str = Field(min_length=1)
    defense: str = Field(min_length=1)
    expected: DefenseVerdict
    observed: DefenseVerdict
    code: str = ""
    passed: bool = False
    detail: str = ""


class SecurityAdversarialReport(VersionedContract):
    """§25 the adversarial corpus verdict — local, no external calls."""

    schema: Literal["apiforge/security-adversarial-report/v1"] = (
        "apiforge/security-adversarial-report/v1"  # type: ignore[assignment]
    )
    cases: tuple[AdversarialCaseResult, ...] = ()
    totals: dict[str, int] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()


class MemoryEvalCaseResult(VersionedContract):
    """§24 one memory-axis case verdict."""

    schema: Literal["apiforge/memory-eval-case-result/v1"] = "apiforge/memory-eval-case-result/v1"  # type: ignore[assignment]
    case_id: str = Field(min_length=1)
    axis: str = Field(min_length=1)
    expected: str = Field(min_length=1)
    observed: str = Field(min_length=1)
    passed: bool = False
    detail: str = ""


class MemoryEvalReport(VersionedContract):
    """§24 the memory corpus verdict across the declared axes."""

    schema: Literal["apiforge/memory-eval-report/v1"] = "apiforge/memory-eval-report/v1"  # type: ignore[assignment]
    cases: tuple[MemoryEvalCaseResult, ...] = ()
    totals: dict[str, int] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()


__all__ = [
    "AdversarialCaseResult",
    "DefenseVerdict",
    "FrontierPoint",
    "LiveEvalLayer",
    "LiveEvalReport",
    "MemoryEvalCaseResult",
    "MemoryEvalReport",
    "ProviderTier",
    "QualityFrontier",
    "SecurityAdversarialReport",
    "TraceGrade",
    "TraceGradeDimension",
    "TraceGradingReport",
    "TraceVerdict",
]
