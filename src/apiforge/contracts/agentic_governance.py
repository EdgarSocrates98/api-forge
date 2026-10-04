"""Contracts for deterministic hierarchical agentic budget admission."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.economy import CostVector
from apiforge.core.models import JsonValue, Sha256, freeze_json

BudgetScope = Literal["task", "phase", "role", "tool"]
BudgetAction = Literal["allow", "stop", "unresolved", "deduplicated"]
BudgetTokenPolicy = Literal["observed_only"]
DecisionRisk = Literal[
    "read_only", "local_reversible", "sensitive", "external_mutation", "destructive", "irreversible"
]
DecisionOutcome = Literal["allow", "review", "block"]


class BudgetLimit(VersionedContract):
    """One hard limit attached to an exact task, phase, role or tool id."""

    scope: BudgetScope
    scope_id: str = Field(min_length=1)
    max_calls: int | None = Field(default=None, ge=0)
    max_context_bytes: int | None = Field(default=None, ge=0)
    max_tool_result_bytes: int | None = Field(default=None, ge=0)
    max_expansions: int | None = Field(default=None, ge=0)
    max_duration_ms: int | None = Field(default=None, ge=0)
    max_observed_tokens: int | None = Field(default=None, ge=0)
    protected: bool = False

    @model_validator(mode="after")
    def has_dimension(self) -> BudgetLimit:
        if not any(
            value is not None
            for value in (
                self.max_calls,
                self.max_context_bytes,
                self.max_tool_result_bytes,
                self.max_expansions,
                self.max_duration_ms,
                self.max_observed_tokens,
            )
        ):
            raise ValueError("a budget limit must declare at least one dimension")
        return self


class AgenticBudgetPlan(VersionedContract):
    """Immutable hierarchical limits for one task and its descendants."""

    schema: Literal["apiforge/agentic-budget-plan/v1"] = "apiforge/agentic-budget-plan/v1"  # type: ignore[assignment]
    plan_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    limits: tuple[BudgetLimit, ...] = Field(min_length=1)
    on_exhaustion: Literal["unresolved"] = "unresolved"
    token_policy: BudgetTokenPolicy = "observed_only"
    created_at: str = Field(min_length=1)
    metadata: dict[str, JsonValue] = Field(default_factory=dict)
    content_sha256: Sha256

    @model_validator(mode="after")
    def validate_limits(self) -> AgenticBudgetPlan:
        keys = [(item.scope, item.scope_id) for item in self.limits]
        if len(keys) != len(set(keys)):
            raise ValueError("budget limits must have unique scope/scope_id pairs")
        if not any(item.scope == "task" and item.scope_id == self.task_id for item in self.limits):
            raise ValueError("budget plan requires a task root limit")
        return self

    @classmethod
    def with_frozen_metadata(cls, **kwargs: object) -> AgenticBudgetPlan:
        metadata = freeze_json(kwargs.pop("metadata", {}))
        return cls(metadata=metadata, **kwargs)  # type: ignore[arg-type]


class BudgetSpend(VersionedContract):
    """One measured, append-only spend receipt attributed to a hierarchy."""

    schema: Literal["apiforge/budget-spend/v1"] = "apiforge/budget-spend/v1"  # type: ignore[assignment]
    spend_id: str = Field(min_length=1)
    plan_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    phase: str = Field(min_length=1)
    role: str = Field(min_length=1)
    tool: str = Field(min_length=1)
    cost: CostVector
    observed_at: str = Field(min_length=1)
    provenance: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


class BudgetDecision(VersionedContract):
    """Admission result; stop and unresolved states are never silent."""

    schema: Literal["apiforge/budget-decision/v1"] = "apiforge/budget-decision/v1"  # type: ignore[assignment]
    action: BudgetAction
    plan_id: str
    task_id: str
    spend_id: str
    recorded: bool = False
    code: str | None = None
    field: str | None = None
    unlock: str | None = None
    reason: str = ""
    exhausted: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    remaining: dict[str, int | None] = Field(default_factory=dict)


class DecisionRequest(VersionedContract):
    """A proposed action; it is not authorization."""

    schema: Literal["apiforge/decision-request/v1"] = "apiforge/decision-request/v1"  # type: ignore[assignment]
    request_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    risk: DecisionRisk
    proposed_by: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()
    requested_at: str = Field(min_length=1)


class DecisionGateResult(VersionedContract):
    """Policy/approval decision with explicit safe unlocks."""

    schema: Literal["apiforge/decision-gate-result/v1"] = "apiforge/decision-gate-result/v1"  # type: ignore[assignment]
    request_id: str
    task_id: str
    run_id: str
    action: str
    risk: DecisionRisk
    outcome: DecisionOutcome
    approval_id: str | None = None
    code: str | None = None
    field: str | None = None
    unlock: str | None = None
    reason: str = ""
    evidence_refs: tuple[str, ...] = ()


# --- step11 phase 4: Agent Governor / gain / stop / recovery / loop (§23-§27)

GovernorProfile = Literal["economy", "balanced", "deep"]
GovernorComplexity = Literal["micro", "low", "medium", "high"]
GovernorSecurityState = Literal["clean", "tainted", "quarantined"]
ExecutionMode = Literal["deterministic", "sandbox", "provider"]
GainAction = Literal[
    "spawn_agent", "call_reviewer", "start_debate", "expand_context", "expensive_retrieval"
]
FailureClass = Literal[
    "missing_evidence",
    "invalid_input",
    "timeout",
    "provider_failure",
    "tool_failure",
    "policy_conflict",
    "budget_exhausted",
    "security_refusal",
    "strategy_failure",
    "deterministic_conflict",
]
RecoveryAction = Literal["retry", "replan", "fallback", "escalate", "stop"]


class GovernorInputs(VersionedContract):
    """§23 governor inputs; missing signals are carried, not guessed."""

    schema: Literal["apiforge/governor-inputs/v1"] = "apiforge/governor-inputs/v1"  # type: ignore[assignment]
    profile: GovernorProfile
    risk: DecisionRisk
    confidence: float | None = Field(default=None, ge=0, le=1)
    evidence_completeness: float | None = Field(default=None, ge=0, le=1)
    context_sufficiency: float | None = Field(default=None, ge=0, le=1)
    budget_remaining: dict[str, int | float | None] = Field(default_factory=dict)
    security_state: GovernorSecurityState = "clean"
    task_complexity: GovernorComplexity | None = None


class GovernorDecision(VersionedContract):
    """§23 ceilings a run must respect; clamps and gaps are explicit."""

    schema: Literal["apiforge/governor-decision/v1"] = "apiforge/governor-decision/v1"  # type: ignore[assignment]
    profile: GovernorProfile
    risk: DecisionRisk
    max_agents: int = Field(ge=0)
    max_reviewers: int = Field(ge=0)
    max_debates: int = Field(ge=0)
    max_retries: int = Field(ge=0)
    max_replans: int = Field(ge=0)
    max_tokens: int | None = Field(default=None, ge=0)
    max_cost: float | None = Field(default=None, ge=0)
    allowed_execution_modes: tuple[ExecutionMode, ...] = ()
    allowed_tools: tuple[str, ...] = ()
    clamped_by: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class ExpectedInformationGain(VersionedContract):
    """§24 pre-action expected gain; a scored signal bundle, never a guess.

    ``score`` is the weighted mean over present signals; signals the caller
    did not supply land in ``unresolved`` and are dropped from the mean —
    the contract never silently treats them as zero.
    """

    schema: Literal["apiforge/expected-information-gain/v1"] = (
        "apiforge/expected-information-gain/v1"  # type: ignore[assignment]
    )
    action: GainAction
    score: float | None = Field(default=None, ge=0, le=1)
    level: Literal["low", "medium", "high", "unresolved"]
    signals: dict[str, float | None] = Field(default_factory=dict)
    reason: str = ""
    unresolved: tuple[str, ...] = ()


class StopDecision(VersionedContract):
    """§25 explicit STOP: continue only on expected gain or requirement."""

    schema: Literal["apiforge/stop-decision/v1"] = "apiforge/stop-decision/v1"  # type: ignore[assignment]
    decision: Literal["continue", "stop"]
    expected_gain: float | None = Field(default=None, ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    mandatory_requirement: bool = False
    reason: str = ""
    code: str | None = None


class RecoveryDecision(VersionedContract):
    """§26 governed recovery for a classified failure."""

    schema: Literal["apiforge/recovery-decision/v1"] = "apiforge/recovery-decision/v1"  # type: ignore[assignment]
    failure_class: FailureClass
    decision: RecoveryAction
    attempt: int = Field(ge=0)
    max_attempts: int = Field(default=0, ge=0)
    reason: str = ""
    code: str | None = None
    unresolved: tuple[str, ...] = ()


class LoopDetection(VersionedContract):
    """§27 repeated-strategy detection over a fingerprint window."""

    schema: Literal["apiforge/loop-detection/v1"] = "apiforge/loop-detection/v1"  # type: ignore[assignment]
    strategy_fingerprint: str = Field(min_length=1)
    repeats: int = Field(ge=0)
    window: int = Field(ge=1)
    blocked: bool = False
    code: str | None = None
    reason: str = ""


# --- step11 phase 5: Decision Control Plane lifecycle (§28-§32)

ControlPlaneMode = Literal["shadow", "assisted", "active"]
FallbackTrigger = Literal[
    "low_confidence", "missing_evidence", "security_issue", "provider_issue", "budget_issue"
]


class ControlPlaneRoute(VersionedContract):
    """§28 a route under lifecycle governance; mode is the latest state."""

    schema: Literal["apiforge/control-plane-route/v1"] = "apiforge/control-plane-route/v1"  # type: ignore[assignment]
    route: str = Field(min_length=1)
    mode: ControlPlaneMode = "shadow"
    candidate: str = Field(min_length=1)
    legacy: str = Field(min_length=1)
    fallback_route: str | None = None
    promoted_at: str | None = None
    promotion_approval_id: str | None = None


class ShadowRecord(VersionedContract):
    """§29 parallel-run record: the candidate never governs in shadow."""

    schema: Literal["apiforge/shadow-record/v1"] = "apiforge/shadow-record/v1"  # type: ignore[assignment]
    route: str = Field(min_length=1)
    candidate_decision: dict[str, object] = Field(default_factory=dict)
    legacy_decision: dict[str, object] = Field(default_factory=dict)
    difference: tuple[str, ...] = ()
    confidence: float | None = Field(default=None, ge=0, le=1)
    evidence_refs: tuple[str, ...] = ()
    recorded_at: str = Field(min_length=1)


class PromotionEvidence(VersionedContract):
    """§31 the five promotion requirements; each is a declared fact."""

    schema: Literal["apiforge/promotion-evidence/v1"] = "apiforge/promotion-evidence/v1"  # type: ignore[assignment]
    route: str = Field(min_length=1)
    eval_thresholds_passed: bool = False
    security_gates_passed: bool = False
    evidence_complete: bool = False
    rollback_exists: bool = False
    approval_id: str | None = None
    evidence_refs: tuple[str, ...] = ()


class PromotionDecision(VersionedContract):
    """Whether a route may move one lifecycle step; never skips a stage."""

    schema: Literal["apiforge/promotion-decision/v1"] = "apiforge/promotion-decision/v1"  # type: ignore[assignment]
    route: str = Field(min_length=1)
    from_mode: ControlPlaneMode
    to_mode: ControlPlaneMode
    allowed: bool = False
    missing: tuple[str, ...] = ()
    code: str | None = None
    reason: str = ""


class FallbackDecision(VersionedContract):
    """§32 every active route needs a declared fallback when degraded."""

    schema: Literal["apiforge/fallback-decision/v1"] = "apiforge/fallback-decision/v1"  # type: ignore[assignment]
    route: str = Field(min_length=1)
    trigger: FallbackTrigger | None = None
    action: Literal["continue_active", "use_fallback", "refuse"]
    fallback_route: str | None = None
    code: str | None = None
    reason: str = ""


class RouteDecision(VersionedContract):
    """Which decision stream governs an evaluation, per §29-§32 mode."""

    schema: Literal["apiforge/route-decision/v1"] = "apiforge/route-decision/v1"  # type: ignore[assignment]
    route: str = Field(min_length=1)
    mode: ControlPlaneMode
    governing: Literal["legacy", "candidate", "none"]
    recommendation: dict[str, object] | None = None
    shadow: bool = False
    fallback: FallbackDecision | None = None
    unresolved: tuple[str, ...] = ()
    reason: str = ""


__all__ = [
    "AgenticBudgetPlan",
    "BudgetAction",
    "BudgetDecision",
    "BudgetLimit",
    "BudgetScope",
    "BudgetSpend",
    "BudgetTokenPolicy",
    "ControlPlaneMode",
    "ControlPlaneRoute",
    "DecisionGateResult",
    "DecisionOutcome",
    "DecisionRequest",
    "DecisionRisk",
    "ExecutionMode",
    "ExpectedInformationGain",
    "FailureClass",
    "FallbackDecision",
    "FallbackTrigger",
    "GainAction",
    "GovernorComplexity",
    "GovernorDecision",
    "GovernorInputs",
    "GovernorProfile",
    "GovernorSecurityState",
    "LoopDetection",
    "PromotionDecision",
    "PromotionEvidence",
    "RecoveryAction",
    "RecoveryDecision",
    "RouteDecision",
    "ShadowRecord",
    "StopDecision",
]
