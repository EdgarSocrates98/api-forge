"""TaskSpec family: sealed units of agentic work and their outcomes."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, Sha256, freeze_json


class TaskSize(StrEnum):
    S = "S"
    M = "M"
    L = "L"


class TaskRisk(StrEnum):
    READ_ONLY = "read_only"
    LOCAL_REVERSIBLE = "local_reversible"
    SENSITIVE = "sensitive"
    EXTERNAL_MUTATION = "external_mutation"
    DESTRUCTIVE = "destructive"
    IRREVERSIBLE = "irreversible"


class Recipe(StrEnum):
    DIRECT = "direct"
    TEST_FIRST = "test-first"
    PLAN_EXECUTE_VERIFY = "plan-execute-verify"
    DIAGNOSE_REPAIR_VERIFY = "diagnose-repair-verify"
    RESEARCH_SYNTHESIZE_VERIFY = "research-synthesize-verify"
    BUILD_ENDPOINT = "build-endpoint"
    VERIFIED_API_SLICE = "verified-api-slice"


class TaskState(StrEnum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    SEALED = "sealed"
    READY = "ready"
    RUNNING = "running"
    PARKED = "parked"
    AWAITING_SUPERVISION = "awaiting_supervision"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"
    EXPIRED = "expired"


class Budgets(VersionedContract):
    """Hard bounds on a task run — calls, rounds, deadline (ISO8601)."""

    max_calls: int = 20
    max_rounds: int = 3
    deadline: str | None = None


class TaskSpec(VersionedContract):
    """A declared unit of agentic work — scope is closed, never widened at run."""

    id: str
    outcome: str
    size: TaskSize = TaskSize.S
    writable_paths: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    preconditions: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    expected_proofs: tuple[str, ...] = ()
    budgets: Budgets = Field(default_factory=Budgets)
    risk: TaskRisk = TaskRisk.READ_ONLY
    strategy: Recipe = Recipe.DIRECT
    rollback: str = ""
    acceptance_criteria: tuple[str, ...] = ()
    capability_covered: str | None = None
    state: TaskState = TaskState.DRAFT
    revision: int = 0


class TaskRevision(VersionedContract):
    """An immutable snapshot of a task's reviewed content + optional seal.

    The seal is Ed25519 over the canonical revision hash — it proves key
    possession at seal time, and any content change produces a new revision
    with a different hash, invalidating the seal by construction.
    """

    task_id: str
    revision: int
    content_sha256: Sha256
    changed_fields: tuple[str, ...] = ()
    sealed_by: str | None = None
    seal_signature_b64: str | None = None
    public_key_sha256: Sha256 | None = None

    @model_validator(mode="after")
    def seal_is_complete_or_absent(self) -> TaskRevision:
        parts = (self.sealed_by, self.seal_signature_b64, self.public_key_sha256)
        if any(p is not None for p in parts) and not all(parts):
            raise ValueError("seal requires sealed_by + signature + key fingerprint")
        return self


class TaskPlan(VersionedContract):
    """The recipe instantiated for a task — ordered verbs with bound inputs."""

    task_id: str
    revision: int
    recipe: Recipe
    steps: tuple[Mapping[str, JsonValue], ...] = ()
    plan_digest: Sha256 | None = None
    proof_axes: tuple[str, ...] = ()

    @field_validator("steps", mode="after")
    @classmethod
    def freeze_steps(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, tuple):
            raise ValueError("steps must be a list of objects")  # noqa: TRY004
        return frozen


class TaskHandoff(VersionedContract):
    """A recorded dispatch: who handed what context to which executor."""

    task_id: str
    revision: int
    from_agent: str
    to_executor: str
    context: tuple[str, ...] = ()
    dispatched_at: str | None = None


class AcceptanceRecord(VersionedContract):
    """Acceptance — recorded by an identity distinct from the executor."""

    task_id: str
    revision: int
    verdict: Literal["accepted", "rejected"]
    accepted_by: str
    executed_by: str | None = None
    evidence: tuple[str, ...] = ()
    notes: str = ""

    @model_validator(mode="after")
    def acceptor_is_not_executor(self) -> AcceptanceRecord:
        if self.executed_by is not None and self.accepted_by == self.executed_by:
            raise ValueError("acceptance must be separate from the executor")
        return self


class CapabilityProof(VersionedContract):
    """Which capability a test/bench actually proves, and to what extent."""

    capability: str
    proven_by: str
    scope: str = ""
    evidence: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class BriefStatus(StrEnum):
    DONE = "DONE"
    REVIEW = "REVIEW"
    DECIDE = "DECIDE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class OutcomeBrief(VersionedContract):
    """The closing brief — DONE is refused while mandatory gaps exist."""

    status: BriefStatus
    outcome: str
    human_action: str | None = None
    proof: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    next: str | None = None
    open: tuple[str, ...] = ()
    subject: str | None = None

    @model_validator(mode="after")
    def done_requires_clean(self) -> OutcomeBrief:
        if self.status is BriefStatus.DONE:
            missing: list[str] = []
            if not self.proof:
                missing.append("proof")
            if self.gaps:
                missing.append("gaps must be empty")
            if self.human_action:
                missing.append("human_action must be absent")
            if self.open:
                missing.append("open must be empty")
            if missing:
                raise ValueError(f"DONE refused: {'; '.join(missing)}")
        return self
