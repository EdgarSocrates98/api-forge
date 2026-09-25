"""Versioned contracts for the provider-neutral agentic runtime."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel
from apiforge.contracts.knowledge import FreshnessState
from apiforge.core.models import JsonValue, Sha256, freeze_json


class AgenticState(StrEnum):
    CREATED = "created"
    TASK_REVIEWED = "task_reviewed"
    PLANNED = "planned"
    RUNNING = "running"
    DEBATING = "debating"
    AWAITING_SUPERVISION = "awaiting_supervision"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class InvocationStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ArtifactKind(StrEnum):
    REVIEW = "review"
    PLAN = "plan"
    SPECIALIST = "specialist"
    CRITIC = "critic"
    DECISION = "decision"
    VERIFICATION = "verification"


class AgenticRun(VersionedContract):
    run_id: str
    task_id: str
    revision: int
    state: AgenticState
    policy_id: str
    invocation_ids: tuple[str, ...] = ()
    artifact_ids: tuple[str, ...] = ()
    decision_ids: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    control_run_id: str | None = None
    verification_evidence: tuple[str, ...] = ()
    eval_status: Literal["not_run", "passed", "review", "blocked"] = "not_run"
    final_status: Literal["DONE", "REVIEW", "BLOCKED"] | None = None
    started_at: str
    finished_at: str | None = None
    run_digest: Sha256 | None = None
    evidence_level: EvidenceLevel = "unknown"


class RuntimeReview(VersionedContract):
    review_id: str
    task_id: str
    revision: int
    reviewer: str
    status: Literal["approved", "review", "blocked"]
    finding_codes: tuple[str, ...] = ()
    finding_messages: tuple[str, ...] = ()
    content_sha256: Sha256
    evidence_level: EvidenceLevel = "unknown"


class AgenticPolicy(VersionedContract):
    policy_id: str
    max_parallel_agents: int = Field(default=4, ge=1, le=64)
    max_calls: int = Field(default=20, ge=1)
    max_rounds: int = Field(default=3, ge=1)
    timeout_seconds: int = Field(default=120, ge=1)
    max_retries: int = Field(default=2, ge=0)
    allow_external_mutation: bool = False
    critic_risks: tuple[str, ...] = (
        "sensitive",
        "external_mutation",
        "destructive",
        "irreversible",
    )
    human_gate_reasons: tuple[str, ...] = (
        "external_mutation",
        "destructive",
        "irreversible",
        "unresolved_debate",
        "low_confidence",
    )
    debate_triggers: tuple[str, ...] = (
        "conflicting_evidence",
        "high_risk",
        "low_confidence",
        "user_requested",
    )
    adapter: str = "fake"
    replay_normalize: bool = True
    redact_sensitive: bool = True
    evidence_level: EvidenceLevel = "declared"

    @model_validator(mode="after")
    def mutation_requires_gate(self) -> AgenticPolicy:
        if self.allow_external_mutation and "external_mutation" not in self.human_gate_reasons:
            raise ValueError("external mutation requires an approval gate")
        return self


class AgentInvocation(VersionedContract):
    invocation_id: str
    run_id: str
    agent: str
    capability: str
    adapter: str
    model: str | None = None
    status: InvocationStatus = InvocationStatus.PENDING
    dependencies: tuple[str, ...] = ()
    input_refs: tuple[str, ...] = ()
    output_artifact_id: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    duration_ms: int | None = None
    retry_count: int = 0
    error_code: str | None = None
    idempotency_key: str | None = None
    checkpoint_sha256: Sha256 | None = None
    result_sha256: Sha256 | None = None
    evidence_level: EvidenceLevel = "unknown"


class AgentCapabilityProfile(VersionedContract):
    profile_id: str
    agent: str
    capabilities: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    quality_axes: tuple[str, ...] = ()
    expertise_packs: tuple[str, ...] = ()
    accepted_risks: tuple[str, ...] = ("read_only",)
    adapter: str = "fake"
    enabled: bool = True
    evidence_level: EvidenceLevel = "declared"


class AgentScorecard(VersionedContract):
    agent: str
    profile_id: str
    evaluation_count: int = Field(default=0, ge=0)
    passed_count: int = Field(default=0, ge=0)
    quality_score: float = Field(default=0.0, ge=0, le=1)
    quality_promoted: bool = False
    observed_cost: float | None = Field(default=None, ge=0)
    observed_duration_ms: float | None = Field(default=None, ge=0)
    observed_tokens: float | None = Field(default=None, ge=0)
    dimension_scores: dict[str, float] = Field(default_factory=dict)
    freshness_state: FreshnessState = "unknown"
    observed_at: str | None = None
    expires_at: str | None = None
    observation_refs: tuple[str, ...] = ()
    last_verdict: Literal["unknown", "PASS", "REVIEW", "BLOCKED"] = "unknown"
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    computed_from: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "unknown"


class AgentArtifact(VersionedContract):
    artifact_id: str
    run_id: str
    invocation_id: str
    agent: str
    capability: str
    kind: ArtifactKind
    schema_name: str
    payload: JsonValue
    evidence: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    confidence: float | None = Field(default=None, ge=0, le=1)
    content_sha256: Sha256
    evidence_level: EvidenceLevel = "unknown"

    @model_validator(mode="after")
    def payload_is_frozen(self) -> AgentArtifact:
        freeze_json(self.payload)
        return self


class HandoffRecord(VersionedContract):
    handoff_id: str
    run_id: str
    from_agent: str
    to_agent: str
    reason: str
    context_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    created_at: str
    evidence_level: EvidenceLevel = "unknown"


class DecisionRecord(VersionedContract):
    decision_id: str
    run_id: str
    question: str
    options: tuple[str, ...] = ()
    chosen: str | None = None
    status: Literal["resolved", "unresolved", "awaiting_supervision"]
    evidence: tuple[str, ...] = ()
    dissent: tuple[str, ...] = ()
    referee: str | None = None
    reason: str = ""
    evidence_level: EvidenceLevel = "unknown"


class ApprovalGate(VersionedContract):
    gate_id: str
    run_id: str
    reason: str
    requested_action: str
    status: Literal["pending", "approved", "rejected"] = "pending"
    requested_by: str
    decided_by: str | None = None
    evidence: tuple[str, ...] = ()
    decision_note: str = ""
    evidence_level: EvidenceLevel = "unknown"


class TrajectoryEvent(VersionedContract):
    event_id: str
    run_id: str
    event: str
    actor: str
    subject: str | None = None
    payload: JsonValue = Field(default_factory=dict)
    created_at: str
    evidence_level: EvidenceLevel = "unknown"
