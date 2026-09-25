"""Versioned contracts for deterministic capability routing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import AliasChoices, Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.risk_complexity import (
    RiskComplexityAssessment,
    RiskComplexityPolicy,
    default_risk_complexity_policy,
)
from apiforge.contracts.scorecard_routing import (
    ScorecardRoutingAssessment,
    ScorecardRoutingPolicy,
    default_scorecard_routing_policy,
)
from apiforge.contracts.scorecard_shadow import ScorecardShadowEvaluation

RoutingSignalName = Literal["cost", "duration", "quality", "security"]
SignalStatus = Literal["observed", "unknown", "unresolved"]
RoutingObjective = Literal["efficiency", "quality"]
RoutingExecutionMode = Literal["parallel_review", "sequential_failover"]
SignalFreshness = Literal["fresh", "stale", "unresolved", "unknown"]


class ObservedSignal(VersionedContract):
    """A routing signal with explicit provenance and unknown-state semantics."""

    name: RoutingSignalName
    value: float | None = Field(default=None, ge=0)
    status: SignalStatus = "unknown"
    unit: str = ""
    source: str = "unknown"
    evidence_refs: tuple[str, ...] = ()
    freshness_state: SignalFreshness = "unknown"
    observed_at: str | None = None
    expires_at: str | None = None

    @model_validator(mode="after")
    def observed_values_are_present(self) -> ObservedSignal:
        if self.status == "observed" and self.value is None:
            raise ValueError("observed routing signals require a value")
        if self.status != "observed" and self.value is not None:
            raise ValueError("unknown or unresolved routing signals cannot carry a value")
        return self


class RoutingPolicy(VersionedContract):
    """Configuration for the bounded first routing policy."""

    policy_id: str
    policy_version: str
    objective_order: tuple[RoutingObjective, ...] = ("efficiency", "quality")
    security_mode: Literal["gate"] = "gate"
    unknown_signal: Literal["unresolved"] = "unresolved"
    tie_breaker: Literal["capability"] = "capability"
    scorecard_update: Literal["eval_required"] = "eval_required"
    execution_mode: RoutingExecutionMode = "parallel_review"
    max_fallbacks: int = Field(default=1, ge=0, le=64)
    risk_complexity: RiskComplexityPolicy = Field(default_factory=default_risk_complexity_policy)
    scorecard_adaptation: ScorecardRoutingPolicy = Field(
        default_factory=default_scorecard_routing_policy
    )

    @model_validator(mode="after")
    def objectives_are_unique(self) -> RoutingPolicy:
        if len(set(self.objective_order)) != len(self.objective_order):
            raise ValueError("routing objective_order must not contain duplicates")
        return self


class RoutingRequest(VersionedContract):
    """Normalized task inputs consumed by eligibility and ranking."""

    task_id: str
    revision: int = Field(ge=0)
    risk: str
    requested_capabilities: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    available_evidence: tuple[str, ...] = ()
    required_expertise: tuple[str, ...] = ()
    available_expertise: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    task_size: Literal["S", "M", "L"] | None = Field(
        default=None,
        validation_alias=AliasChoices("task_size", "size"),
    )
    dependencies: tuple[str, ...] = ()
    expected_proofs: tuple[str, ...] = ()
    strategy: str | None = None
    policy_id: str


class CandidateAssessment(VersionedContract):
    """Explainable eligibility and ranking state for one candidate."""

    capability: str
    agent: str
    eligible: bool
    rejection: Mapping[str, str] | None = None
    signals: tuple[ObservedSignal, ...] = ()
    ranking_key: tuple[str, ...] = ()
    family: str | None = None
    implementation: str | None = None
    expertise_packs: tuple[str, ...] = ()


class RoutingDecision(VersionedContract):
    """Persisted routing trace and deterministic execution order."""

    decision_id: str
    task_id: str
    revision: int = Field(ge=0)
    policy_id: str
    candidates: tuple[CandidateAssessment, ...] = ()
    selected: str | None = None
    fallback_order: tuple[str, ...] = ()
    risk_complexity: RiskComplexityAssessment | None = None
    scorecard_routing: ScorecardRoutingAssessment | None = None
    shadow_evaluation: ScorecardShadowEvaluation | None = None
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class RoutingPlan(VersionedContract):
    """Explicit, bounded execution roles derived from a routing decision."""

    plan_id: str
    decision_id: str
    task_id: str
    revision: int = Field(ge=0)
    primary: str | None = None
    fallbacks: tuple[str, ...] = ()
    parallel: tuple[str, ...] = ()
    reviewers: tuple[str, ...] = ()
    critic: str | None = None
    referee: str | None = None
    execution_mode: RoutingExecutionMode = "parallel_review"
    max_fallbacks: int = Field(default=1, ge=0, le=64)
    assessment_id: str | None = None
    complexity: str | None = None
    verification_depth: str | None = None
    required_roles: tuple[str, ...] = ()
    gate_state: str = "open"
    challenger_order: tuple[str, ...] = ()
    challenger_slots: int = Field(default=0, ge=0, le=8)
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()

    @model_validator(mode="after")
    def roles_are_disjoint_and_bounded(self) -> RoutingPlan:
        roles: list[tuple[str, str]] = []
        if self.primary is not None:
            roles.append(("primary", self.primary))
        roles.extend(("fallback", item) for item in self.fallbacks)
        roles.extend(("parallel", item) for item in self.parallel)
        roles.extend(("reviewer", item) for item in self.reviewers)
        if self.critic is not None:
            roles.append(("critic", self.critic))
        if self.referee is not None:
            roles.append(("referee", self.referee))
        names = [name for _, name in roles]
        if len(set(names)) != len(names):
            raise ValueError("routing plan roles must not contain duplicate capabilities")
        if len(self.fallbacks) > self.max_fallbacks:
            raise ValueError("routing plan fallbacks exceed max_fallbacks")
        return self


class ScorecardFeedback(VersionedContract):
    """Decision artifact for an evidence-gated scorecard update."""

    profile_id: str
    status: Literal["updated", "not_updated", "blocked"]
    gate_status: str
    scorecard_path: str | None = None
    eval_refs: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
