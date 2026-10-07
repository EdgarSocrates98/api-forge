"""Selective-agentics contracts: lazy expertise, per-role context, debate deltas, shadow, audit."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.trust import TrustUnit

ContextClass = Literal[
    "focused", "evidence_plus_delta", "decision_plus_evidence", "disagreements_only"
]
RoleKind = Literal["specialist", "reviewer", "critic", "referee"]


class ExpertisePick(VersionedContract):
    """One knowledge pack selected for a request and the trigger that selected it."""

    pack_id: str = Field(min_length=1)
    pack_version: int = Field(ge=1)
    reasons: tuple[str, ...] = ()
    bytes: int = Field(default=0, ge=0)


class ExpertiseSelection(VersionedContract):
    """Lazy expertise: only packs a declared trigger names; no trigger means no packs."""

    schema: Literal["apiforge/expertise-selection/v1"] = "apiforge/expertise-selection/v1"  # type: ignore[assignment]
    intent: str = ""
    capability: str | None = None
    frameworks: tuple[str, ...] = ()
    selected: tuple[ExpertisePick, ...] = ()
    loaded_bytes: int = Field(default=0, ge=0)
    catalog_bytes: int = Field(default=0, ge=0)
    catalog_packs: int = Field(default=0, ge=0)
    unresolved: tuple[str, ...] = ()


class RoleContext(VersionedContract):
    """What one invocation receives: its class, refs, bytes and budget.

    ``trust_units`` records the §8 TrustUnit admission decision per admitted
    ref/artifact — the run can prove which trust/taint posture each context
    unit carried instead of asserting it after the fact.
    """

    role: RoleKind
    capability: str = Field(min_length=1)
    context_class: ContextClass
    refs: tuple[str, ...] = ()
    artifact_refs: tuple[str, ...] = ()
    expertise: tuple[str, ...] = ()
    bytes: int = Field(default=0, ge=0)
    budget_bytes: int = Field(default=0, ge=0)
    pool_bytes: int | None = Field(default=None, ge=0)
    trimmed: tuple[str, ...] = ()
    prompt_prefix_sha256: str | None = None
    trust_units: tuple[TrustUnit, ...] = ()

    @model_validator(mode="after")
    def bytes_within_budget(self) -> RoleContext:
        if self.bytes > self.budget_bytes:
            raise ValueError("role bytes exceed its budget_bytes")
        if self.pool_bytes is not None and self.budget_bytes > self.pool_bytes:
            raise ValueError("role budget_bytes exceed its class pool")
        return self


class RoleContextPlan(VersionedContract):
    """Per-role subsets of one shared capsule (§86–87)."""

    schema: Literal["apiforge/role-context-plan/v1"] = "apiforge/role-context-plan/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    target: str | None = None
    capsule_id: str | None = None
    context_bytes: int = Field(ge=0)
    roles: tuple[RoleContext, ...] = ()
    total_bytes: int = Field(default=0, ge=0)
    naive_bytes: int = Field(default=0, ge=0)
    unresolved: tuple[str, ...] = ()

    @model_validator(mode="after")
    def within_envelope(self) -> RoleContextPlan:
        """``BudgetEnvelope.context_bytes`` is a hard global budget, not a per-role hint."""
        if self.total_bytes != sum(row.bytes for row in self.roles):
            raise ValueError("total_bytes must equal the sum of role bytes")
        if self.total_bytes > self.context_bytes:
            raise ValueError("total_bytes exceeds BudgetEnvelope.context_bytes")
        pools: dict[str, int] = {}
        for row in self.roles:
            if row.pool_bytes is not None:
                pools[row.context_class] = pools.get(row.context_class, 0) + row.budget_bytes
                if pools[row.context_class] > row.pool_bytes:
                    raise ValueError(f"class {row.context_class} budgets exceed its pool")
        return self


class Disagreement(VersionedContract):
    point: str = Field(min_length=1)
    reason: str = ""


class PositionDelta(VersionedContract):
    """A debate position as a contract, not prose (§32, §84)."""

    side: str = Field(min_length=1)
    position: str = Field(min_length=1)
    evidence: tuple[str, ...] = ()
    disagreements: tuple[Disagreement, ...] = ()
    risks: tuple[str, ...] = ()
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class RefereePacket(VersionedContract):
    """Referee input: the shared capsule id plus deltas and the disagreement set only."""

    schema: Literal["apiforge/referee-packet/v1"] = "apiforge/referee-packet/v1"  # type: ignore[assignment]
    debate_id: str = Field(min_length=1)
    question: str = ""
    capsule_id: str | None = None
    positions: tuple[PositionDelta, ...] = ()
    disagreements: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    packet_bytes: int = Field(default=0, ge=0)
    naive_bytes: int = Field(default=0, ge=0)


class ShadowDecision(VersionedContract):
    """Bounded challenger shadow (§36–38): observational, never part of the result."""

    schema: Literal["apiforge/shadow-decision/v1"] = "apiforge/shadow-decision/v1"  # type: ignore[assignment]
    share: float = Field(ge=0.0, le=0.5)
    mode: Literal["paired_ab", "capability_eval"] = "paired_ab"
    sampled: bool = False
    executed: bool = False
    challenger: str | None = None
    calls: int = Field(default=0, ge=0)
    reason: str = ""
    agreement: bool | None = None
    comparison_ref: str | None = None


class ChallengerSide(VersionedContract):
    """One side of a champion/challenger comparison; ``None`` = unobservable."""

    schema: Literal["apiforge/challenger-side/v1"] = "apiforge/challenger-side/v1"  # type: ignore[assignment]
    capability: str = Field(min_length=1)
    artifact_id: str | None = None
    recommendation: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    facts: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    duration_ms: int | None = Field(default=None, ge=0)
    tool_calls: tuple[str, ...] = ()


class ChallengerComparison(VersionedContract):
    """§53–58 receipt: champion vs challenger over observable fields only.

    The challenger ran in shadow and never governs; this receipt records the
    comparison — promotion remains a control-plane decision over accumulated
    evidence, never implied by a single comparison. A challenger is not a
    fallback: fallbacks execute on failure to produce the authoritative
    result; challengers run beside a healthy champion to be observed.
    """

    schema: Literal["apiforge/challenger-comparison/v1"] = "apiforge/challenger-comparison/v1"  # type: ignore[assignment]
    run_id: str
    task_id: str
    mode: Literal["paired_ab", "capability_eval"]
    champion: ChallengerSide
    challenger: ChallengerSide
    agreement: bool | None = None
    quality_delta: float | None = None
    latency_delta_ms: int | None = None
    token_delta: int | None = None
    cost_delta_usd: float | None = None
    structured_correctness: bool | None = None
    tool_correctness: bool | None = None
    governs: Literal[False] = False
    basis: tuple[str, ...] = ()


class AgentUniqueness(VersionedContract):
    """Anti-agentic-theater gate row (§29): what an agent owns that no other agent does."""

    agent: str = Field(min_length=1)
    capabilities: tuple[str, ...] = ()
    decision_roles: tuple[str, ...] = ()
    rule_areas: tuple[str, ...] = ()
    executors: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    unique_capability: bool = False
    unique_expertise: bool = False
    unique_validator: bool = False
    unique_tool: bool = False
    unique_decision_role: bool = False
    verdict: Literal["keep", "merge-candidate"]
    overlaps: tuple[str, ...] = ()


__all__ = [
    "AgentUniqueness",
    "ChallengerComparison",
    "ChallengerSide",
    "ContextClass",
    "Disagreement",
    "ExpertisePick",
    "ExpertiseSelection",
    "PositionDelta",
    "RefereePacket",
    "RoleContext",
    "RoleContextPlan",
    "RoleKind",
    "ShadowDecision",
]
