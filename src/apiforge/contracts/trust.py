"""Transversal Trust Plane contracts (step11 phase 2, prompt §8–§16).

One trust vocabulary for every context-bearing surface: capsules, memory,
blackboard, knowledge, tool results, MCP responses, handoffs and external
content. The fundamental rule — DATA IS NOT INSTRUCTION — is enforced by the
contracts: only ``system``/``governed_policy`` origins may carry instruction
authority, and propagation never raises authority above its sources.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.agentic_memory import (
    Freshness,
    MemoryConflict,
    MemoryOrigin,
    MemoryQuery,
    TrustLevel,
)
from apiforge.contracts.base import VersionedContract
from apiforge.contracts.context import ContextRef

InstructionAuthority = Literal["system", "policy", "none"]

#: Origins that may carry instruction authority; all others are data.
AUTHORITATIVE_ORIGINS: tuple[MemoryOrigin, ...] = ("system", "governed_policy")

#: Origins whose content is data and can never carry instruction authority.
DATA_ORIGINS: tuple[MemoryOrigin, ...] = (
    "verified_evidence",
    "trusted_internal",
    "knowledge",
    "memory",
    "tool_result",
    "model_generated",
    "user_data",
    "external_data",
    "external_untrusted",
    "unknown",
)

TrustBoundary = Literal[
    "context_capsule",
    "memory",
    "blackboard",
    "knowledge",
    "tool_result",
    "mcp_response",
    "agent_handoff",
    "api_spec",
    "external_content",
    "log",
    "ci_output",
    "documentation",
    "web",
]


class TrustUnit(VersionedContract):
    """The transversal trust annotation carried by any context unit (§8)."""

    schema: Literal["apiforge/trust-unit/v1"] = "apiforge/trust-unit/v1"  # type: ignore[assignment]
    subject: str = Field(min_length=1)
    boundary: TrustBoundary
    origin: MemoryOrigin
    trust_level: TrustLevel = "unknown"
    taint: tuple[str, ...] = ()
    instruction_authority: InstructionAuthority = "none"
    scope: str = ""
    provenance: tuple[str, ...] = ()
    freshness: Freshness = "unknown"
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def authority_requires_authoritative_origin(self) -> TrustUnit:
        """DATA IS NOT INSTRUCTION: data origins never carry authority."""
        if self.instruction_authority != "none" and self.origin not in AUTHORITATIVE_ORIGINS:
            raise ValueError(
                f"origin {self.origin!r} is data and cannot carry instruction authority"
            )
        return self


class TrustedRef(VersionedContract):
    """A ContextCapsule ref annotated with its TrustUnit; the ref is unchanged."""

    ref: ContextRef
    trust: TrustUnit


PropagationTransform = Literal[
    "verbatim",
    "parse_extract",
    "summarize",
    "governed_verification",
    "system_synthesis",
]


class TrustPropagation(VersionedContract):
    """The record of deriving one TrustUnit from sources (§10).

    Taint is the union of source taints; it may only be reduced by a
    ``governed_verification`` transform backed by ``evidence_refs``.
    ``instruction_authority`` never widens: any data source forces ``none``.
    """

    schema: Literal["apiforge/trust-propagation/v1"] = "apiforge/trust-propagation/v1"  # type: ignore[assignment]
    transform: PropagationTransform
    derived: TrustUnit
    derived_from: tuple[str, ...] = ()
    taint_reduced: bool = False
    reason: str = ""


ToolRiskClass = Literal[
    "read_only",
    "write",
    "destructive",
    "reversible",
    "external_side_effect",
    "financial_impact",
    "security_impact",
    "production_impact",
]


class ToolRiskProfile(VersionedContract):
    """Risk classification of one callable tool (§13)."""

    schema: Literal["apiforge/tool-risk-profile/v1"] = "apiforge/tool-risk-profile/v1"  # type: ignore[assignment]
    tool: str = Field(min_length=1)
    risk_classes: tuple[ToolRiskClass, ...] = ()
    reversible: bool = True
    notes: str = ""

    @model_validator(mode="after")
    def has_at_least_one_class(self) -> ToolRiskProfile:
        if not self.risk_classes:
            raise ValueError("a tool risk profile requires at least one risk class")
        return self


class AgentPermissionSet(VersionedContract):
    """Allowlist-first authorization for one agent role/capability (§13).

    Default is DENY: a tool must be named in ``allowed_tools`` *and* every
    class in its risk profile must appear in ``allowed_risk_classes``.
    ``denied_tools`` always wins over both allowlists.
    """

    schema: Literal["apiforge/agent-permission-set/v1"] = "apiforge/agent-permission-set/v1"  # type: ignore[assignment]
    subject: str = Field(min_length=1)
    allowed_tools: tuple[str, ...] = ()
    allowed_risk_classes: tuple[ToolRiskClass, ...] = ()
    denied_tools: tuple[str, ...] = ()
    allowed_targets: tuple[str, ...] = ()
    delegates_to: tuple[str, ...] = ()
    notes: str = ""


class ToolAuthorization(VersionedContract):
    """The recorded authorization decision for one (subject, tool) pair."""

    schema: Literal["apiforge/tool-authorization/v1"] = "apiforge/tool-authorization/v1"  # type: ignore[assignment]
    subject: str = Field(min_length=1)
    tool: str = Field(min_length=1)
    decision: Literal["allow", "deny"]
    risk_classes: tuple[ToolRiskClass, ...] = ()
    code: str | None = None
    field: str | None = None
    unlock: str | None = None
    reason: str = ""


MemoryGateName = Literal[
    "scope",
    "origin",
    "evidence",
    "outcome",
    "freshness",
    "trust",
]
MemoryGateVerdict = Literal["persist", "quarantine", "reject"]


class MemoryGateResult(VersionedContract):
    """The §14 gate pipeline outcome for one MemoryCandidate.

    Order: scope → origin → evidence → trust → outcome → freshness.
    Hard violations reject; borderline trust/freshness states quarantine for
    human review rather than silently persisting or dropping.
    """

    schema: Literal["apiforge/memory-gate-result/v1"] = "apiforge/memory-gate-result/v1"  # type: ignore[assignment]
    candidate_id: str = Field(min_length=1)
    verdict: MemoryGateVerdict
    gates_passed: tuple[MemoryGateName, ...] = ()
    gates_failed: tuple[MemoryGateName, ...] = ()
    quarantine_reasons: tuple[str, ...] = ()
    code: str | None = None
    field: str | None = None
    unlock: str | None = None
    reason: str = ""


class MemoryQuarantine(VersionedContract):
    """A quarantined candidate (or its resolution) in the append-only log (§14)."""

    schema: Literal["apiforge/memory-quarantine/v1"] = "apiforge/memory-quarantine/v1"  # type: ignore[assignment]
    quarantine_id: str = Field(pattern=r"^quarantine:[0-9a-f]{16}$")
    candidate_id: str = Field(min_length=1)
    memory_id: str = Field(min_length=1)
    state: Literal["quarantined", "released"]
    reasons: tuple[str, ...] = ()
    verdict: Literal["persisted", "rejected"] | None = None
    created_at: str
    resolved_by: str | None = None


MemoryInvalidationTrigger = Literal[
    "runtime_change",
    "framework_change",
    "contract_change",
    "policy_change",
    "source_change",
    "contradicting_evidence",
    "outcome_invalid",
    "dependency_change",
]


class MemoryInvalidationPlan(VersionedContract):
    """Advisory §16 invalidation candidates for one trigger.

    Planning only — callers still append `MemoryInvalidation` events through
    `invalidate_memory`; nothing here mutates the store.
    """

    schema: Literal["apiforge/memory-invalidation-plan/v1"] = "apiforge/memory-invalidation-plan/v1"  # type: ignore[assignment]
    trigger: MemoryInvalidationTrigger
    memory_ids: tuple[str, ...] = ()
    rationale: dict[str, str] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()


class MemoryScore(VersionedContract):
    """Score decomposition for one retrieved memory (§15)."""

    memory_id: str = Field(min_length=1)
    score: float = Field(ge=0.0)
    signals: dict[str, float] = Field(default_factory=dict)


class MemoryRankedResult(VersionedContract):
    """A `MemoryRetrievalResult` plus per-record score decomposition."""

    schema: Literal["apiforge/memory-ranked-result/v1"] = "apiforge/memory-ranked-result/v1"  # type: ignore[assignment]
    query: MemoryQuery
    ranked: tuple[MemoryScore, ...] = ()
    conflicts: tuple[MemoryConflict, ...] = ()
    unresolved: tuple[str, ...] = ()


__all__ = [
    "AUTHORITATIVE_ORIGINS",
    "DATA_ORIGINS",
    "AgentPermissionSet",
    "InstructionAuthority",
    "MemoryGateName",
    "MemoryGateResult",
    "MemoryGateVerdict",
    "MemoryInvalidationPlan",
    "MemoryInvalidationTrigger",
    "MemoryQuarantine",
    "MemoryRankedResult",
    "MemoryScore",
    "PropagationTransform",
    "ToolAuthorization",
    "ToolRiskClass",
    "ToolRiskProfile",
    "TrustBoundary",
    "TrustPropagation",
    "TrustUnit",
    "TrustedRef",
]
