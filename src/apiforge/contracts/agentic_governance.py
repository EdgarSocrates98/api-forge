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


__all__ = [
    "AgenticBudgetPlan",
    "BudgetAction",
    "BudgetDecision",
    "BudgetLimit",
    "BudgetScope",
    "BudgetSpend",
    "BudgetTokenPolicy",
    "DecisionGateResult",
    "DecisionOutcome",
    "DecisionRequest",
    "DecisionRisk",
]
