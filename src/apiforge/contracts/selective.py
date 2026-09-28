"""Selective-agentics contracts: lazy expertise, per-role context, debate deltas, shadow, audit."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

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
    """What one invocation receives: its class, refs, bytes and budget."""

    role: RoleKind
    capability: str = Field(min_length=1)
    context_class: ContextClass
    refs: tuple[str, ...] = ()
    artifact_refs: tuple[str, ...] = ()
    expertise: tuple[str, ...] = ()
    bytes: int = Field(default=0, ge=0)
    budget_bytes: int = Field(default=0, ge=0)
    trimmed: tuple[str, ...] = ()


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
    sampled: bool = False
    executed: bool = False
    challenger: str | None = None
    calls: int = Field(default=0, ge=0)
    reason: str = ""
    agreement: bool | None = None


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
