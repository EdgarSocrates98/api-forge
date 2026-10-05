"""Governed memory, blackboard and semantic checkpoint contracts.

These contracts deliberately model agent state as data. None of the payloads
contains an instruction authority field: provenance and trust describe data
quality, while policy decides what a caller may do with the data.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, Sha256, freeze_json

MemoryScope = Literal["working", "case", "task", "episodic", "institutional", "semantic"]
#: Unified origin taxonomy (step11 §8). ``knowledge`` is curated reference
#: material: more trusted than model output, less than verified evidence.
MemoryOrigin = Literal[
    "system",
    "governed_policy",
    "verified_evidence",
    "trusted_internal",
    "knowledge",
    "tool_result",
    "memory",
    "model_generated",
    "user_data",
    "external_data",
    "external_untrusted",
    "unknown",
]
TrustLevel = Literal["unknown", "candidate", "untrusted", "observed", "trusted", "verified"]
Freshness = Literal["fresh", "stale", "unknown", "unresolved"]
MemoryState = Literal["candidate", "persisted", "reinforced", "invalidated", "quarantined"]
MemoryAction = Literal["accepted", "rejected", "invalidated", "deduplicated", "quarantined"]


class MemoryTrust(VersionedContract):
    """Trust decision kept separate from the memory payload."""

    level: TrustLevel = "unknown"
    taint: tuple[str, ...] = ()
    instruction_authority: Literal["none"] = "none"
    evidence_refs: tuple[str, ...] = ()
    reason: str = ""


class MemoryRecord(VersionedContract):
    """A provenance-bound memory item; persisted records are immutable."""

    schema: Literal["apiforge/memory-record/v1"] = "apiforge/memory-record/v1"  # type: ignore[assignment]
    memory_id: str = Field(pattern=r"^memory:[0-9a-f]{16}$")
    scope: MemoryScope
    origin: MemoryOrigin
    created_at: str
    observed_at: str | None = None
    expires_at: str | None = None
    freshness: Freshness = "unknown"
    trust_level: TrustLevel = "unknown"
    provenance: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    environment_fingerprint: str | None = None
    applicability: dict[str, JsonValue] = Field(default_factory=dict)
    runtime_constraints: tuple[str, ...] = ()
    outcome: MemoryState = "candidate"
    confidence: float | None = Field(default=None, ge=0, le=1)
    invalidated_by: str | None = None
    payload: JsonValue = Field(default_factory=dict)
    trust: MemoryTrust = Field(default_factory=MemoryTrust)
    content_sha256: Sha256

    @field_validator("applicability", "payload", mode="after")
    @classmethod
    def freeze_payload(cls, value: object) -> JsonValue:
        return freeze_json(value)

    @model_validator(mode="after")
    def invalidation_has_reason(self) -> MemoryRecord:
        if self.outcome == "invalidated" and not self.invalidated_by:
            raise ValueError("invalidated memory requires invalidated_by")
        if self.outcome != "invalidated" and self.invalidated_by is not None:
            raise ValueError("only invalidated memory may carry invalidated_by")
        return self


class MemoryCandidate(VersionedContract):
    """A proposed memory that still needs policy/evidence validation."""

    schema: Literal["apiforge/memory-candidate/v1"] = "apiforge/memory-candidate/v1"  # type: ignore[assignment]
    candidate_id: str = Field(pattern=r"^candidate:[0-9a-f]{16}$")
    record: MemoryRecord
    proposed_by: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    unresolved: tuple[str, ...] = ()


class MemoryPolicy(VersionedContract):
    """Fail-closed persistence and retrieval policy."""

    policy_id: str = Field(min_length=1)
    allowed_scopes: tuple[MemoryScope, ...] = (
        "working",
        "case",
        "task",
        "episodic",
    )
    minimum_trust: TrustLevel = "observed"
    require_evidence_for_persistent: bool = True
    allow_model_generated_persistent: bool = False
    allow_external_untrusted: bool = False
    max_results: int = Field(default=20, ge=1, le=200)


class MemoryQuery(VersionedContract):
    """Bounded, explicit retrieval request."""

    schema: Literal["apiforge/memory-query/v1"] = "apiforge/memory-query/v1"  # type: ignore[assignment]
    terms: tuple[str, ...] = ()
    scopes: tuple[MemoryScope, ...] = ()
    environment_fingerprint: str | None = None
    now: str | None = None
    minimum_trust: TrustLevel = "unknown"
    include_invalidated: bool = False
    max_results: int = Field(default=20, ge=1, le=200)


class MemoryOutcome(VersionedContract):
    """Result of a policy-gated memory operation."""

    schema: Literal["apiforge/memory-outcome/v1"] = "apiforge/memory-outcome/v1"  # type: ignore[assignment]
    action: MemoryAction
    memory_id: str | None = None
    accepted: bool = False
    code: str | None = None
    field: str | None = None
    unlock: str | None = None
    reason: str = ""
    evidence_refs: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class MemoryRetrievalResult(VersionedContract):
    """Bounded retrieval with freshness and contamination diagnostics."""

    schema: Literal["apiforge/memory-retrieval/v1"] = "apiforge/memory-retrieval/v1"  # type: ignore[assignment]
    query: MemoryQuery
    records: tuple[MemoryRecord, ...] = ()
    stale_count: int = Field(default=0, ge=0)
    invalidated_count: int = Field(default=0, ge=0)
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved"] = "ready"


class MemoryInvalidation(VersionedContract):
    """Append-only invalidation event; it never deletes the original record."""

    schema: Literal["apiforge/memory-invalidation/v1"] = "apiforge/memory-invalidation/v1"  # type: ignore[assignment]
    invalidation_id: str = Field(pattern=r"^invalidation:[0-9a-f]{16}$")
    memory_id: str = Field(pattern=r"^memory:[0-9a-f]{16}$")
    reason: str = Field(min_length=1)
    invalidated_by: str = Field(min_length=1)
    created_at: str
    evidence_refs: tuple[str, ...] = ()


BlackboardKind = Literal[
    "fact",
    "claim",
    "hypothesis",
    "objection",
    "contradiction",
    "evidence",
    "experiment",
    "decision",
    "unknown",
    "handoff",
    "trace",
    "artifact",
]
BlackboardState = Literal["open", "accepted", "rejected", "superseded"]


class BlackboardEntry(VersionedContract):
    """One append-only structured shared-state entry."""

    schema: Literal["apiforge/blackboard-entry/v1"] = "apiforge/blackboard-entry/v1"  # type: ignore[assignment]
    entry_id: str = Field(pattern=r"^blackboard:[0-9a-f]{16}$")
    task_id: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    kind: BlackboardKind
    state: BlackboardState = "open"
    origin: MemoryOrigin
    trust_level: TrustLevel = "unknown"
    taint: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    payload: JsonValue = Field(default_factory=dict)
    created_at: str
    supersedes: tuple[str, ...] = ()
    content_sha256: Sha256

    @field_validator("payload", mode="after")
    @classmethod
    def freeze_payload(cls, value: object) -> JsonValue:
        return freeze_json(value)


class BlackboardQuery(VersionedContract):
    schema: Literal["apiforge/blackboard-query/v1"] = "apiforge/blackboard-query/v1"  # type: ignore[assignment]
    task_id: str = Field(min_length=1)
    kinds: tuple[BlackboardKind, ...] = ()
    scope: str | None = None
    terms: tuple[str, ...] = ()
    max_results: int = Field(default=50, ge=1, le=500)


class BlackboardResult(VersionedContract):
    schema: Literal["apiforge/blackboard-result/v1"] = "apiforge/blackboard-result/v1"  # type: ignore[assignment]
    query: BlackboardQuery
    entries: tuple[BlackboardEntry, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved"] = "ready"


class SemanticCheckpoint(VersionedContract):
    """Resume state independent of transcript compaction."""

    schema: Literal["apiforge/semantic-checkpoint/v1"] = "apiforge/semantic-checkpoint/v1"  # type: ignore[assignment]
    checkpoint_id: str = Field(pattern=r"^checkpoint:[0-9a-f]{16}$")
    task_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    task_state: str = Field(min_length=1)
    current_objective: str = Field(min_length=1)
    decisions_accepted: tuple[str, ...] = ()
    decisions_rejected: tuple[str, ...] = ()
    facts_still_valid: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    working_set: tuple[str, ...] = ()
    artifact_refs: tuple[str, ...] = ()
    memory_refs: tuple[str, ...] = ()
    tool_state: dict[str, JsonValue] = Field(default_factory=dict)
    routing_state: dict[str, JsonValue] = Field(default_factory=dict)
    budget_state: dict[str, JsonValue] = Field(default_factory=dict)
    next_actions: tuple[str, ...] = ()
    risk_state: dict[str, JsonValue] = Field(default_factory=dict)
    created_at: str
    content_sha256: Sha256

    @field_validator("tool_state", "routing_state", "budget_state", "risk_state", mode="after")
    @classmethod
    def freeze_maps(cls, value: object) -> JsonValue:
        return freeze_json(value)


__all__ = [
    "BlackboardEntry",
    "BlackboardKind",
    "BlackboardQuery",
    "BlackboardResult",
    "Freshness",
    "MemoryCandidate",
    "MemoryInvalidation",
    "MemoryOutcome",
    "MemoryPolicy",
    "MemoryQuery",
    "MemoryRecord",
    "MemoryRetrievalResult",
    "MemoryScope",
    "MemoryTrust",
    "SemanticCheckpoint",
    "TrustLevel",
]
