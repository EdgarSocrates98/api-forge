"""Versioned contracts for the Forge Protocol interop layer (prompt §46–§49).

The Forge Protocol is the public façade other engines (The Forger, Spark
Forge) will speak to. v1 is deliberately local: ``submit`` validates and
persists intent, ``attach`` links a governed TaskSpec, and
``inspect``/``result``/``evidence`` project only what the governed runtime
actually produced — nothing is fabricated for the wire.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.platform import CapabilityRisk, CapabilityState
from apiforge.contracts.task import Budgets
from apiforge.core.models import JsonValue, Sha256, freeze_json

# The closed forge-side lifecycle — distinct from the governed TaskState on
# purpose: the wire contract stays small and stable while internals evolve.
ForgeTaskState = Literal[
    "received",
    "accepted",
    "in_progress",
    "completed",
    "failed",
    "refused",
    "unresolved",
]

ForgeResultStatus = Literal["ok", "review", "blocked", "failed", "unresolved"]

PROTOCOL_VERSION: str = "forge-protocol/v1"
ENGINE_NAME: str = "api-forge"


class ForgeCapabilityDescriptor(VersionedContract):
    """§46 public capability projection — the matrix row an engine can call."""

    schema: Literal["apiforge/forge-capability-descriptor/v1"] = (
        "apiforge/forge-capability-descriptor/v1"  # type: ignore[assignment]
    )
    capability_id: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    state: CapabilityState
    risk: CapabilityRisk
    surfaces: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class ForgeTaskRequest(VersionedContract):
    """§46 a task submitted over the wire — intent plus declared constraints."""

    schema: Literal["apiforge/forge-task-request/v1"] = "apiforge/forge-task-request/v1"  # type: ignore[assignment]
    task_id: str = Field(min_length=3, max_length=63, pattern=r"^[a-z0-9][a-z0-9-]{1,62}$")
    capability_id: str = Field(min_length=1)
    intent: str = Field(min_length=1)
    inputs: Mapping[str, JsonValue] = Field(default_factory=dict)
    budgets: Budgets = Field(default_factory=Budgets)
    risk: CapabilityRisk = "read_only"
    origin_engine: str = "api-forge"
    requested_by: str = ""
    requested_at: str = ""

    @field_validator("inputs", mode="after")
    @classmethod
    def freeze_inputs(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("inputs must be a JSON object")
        return frozen


class ForgeTaskStatus(VersionedContract):
    """§46 the wire-visible state of a submitted task and its governed link."""

    schema: Literal["apiforge/forge-task-status/v1"] = "apiforge/forge-task-status/v1"  # type: ignore[assignment]
    task_id: str = Field(min_length=1)
    state: ForgeTaskState
    governed_task_id: str | None = None
    governed_state: str | None = None
    revision: int = Field(default=0, ge=0)
    updated_at: str = ""
    unresolved: tuple[str, ...] = ()


class ForgeTaskResult(VersionedContract):
    """§46 the outcome projection — gaps are named, never hidden."""

    schema: Literal["apiforge/forge-task-result/v1"] = "apiforge/forge-task-result/v1"  # type: ignore[assignment]
    task_id: str = Field(min_length=1)
    status: ForgeResultStatus
    payload: Mapping[str, JsonValue] = Field(default_factory=dict)
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    error_code: str | None = None

    @field_validator("payload", mode="after")
    @classmethod
    def freeze_payload(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("payload must be a JSON object")
        return frozen


class ForgeEvidenceArtifact(VersionedContract):
    """One content-addressed artifact inside an evidence bundle."""

    path: str = Field(min_length=1)
    sha256: Sha256
    kind: str = ""


class ForgeEvidenceBundle(VersionedContract):
    """§46 the portable evidence set for a task — artifacts + hashes only."""

    schema: Literal["apiforge/forge-evidence-bundle/v1"] = "apiforge/forge-evidence-bundle/v1"  # type: ignore[assignment]
    task_id: str = Field(min_length=1)
    artifacts: tuple[ForgeEvidenceArtifact, ...] = ()
    produced_at: str = ""
    unresolved: tuple[str, ...] = ()


class ForgeHandoff(VersionedContract):
    """§46/§48 the portable cross-engine handoff bundle.

    ``delivery`` is always ``prepared`` in v1 — moving the bundle to another
    engine is a human or transport step; the protocol never performs a live
    cross-engine call.
    """

    schema: Literal["apiforge/forge-handoff/v1"] = "apiforge/forge-handoff/v1"  # type: ignore[assignment]
    handoff_id: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    from_engine: str = Field(min_length=1)
    to_engine: str = Field(min_length=1)
    request: ForgeTaskRequest
    status: ForgeTaskStatus | None = None
    evidence_refs: tuple[str, ...] = ()
    context_refs: tuple[str, ...] = ()
    delivery: Literal["prepared"] = "prepared"
    created_at: str = ""
    unresolved: tuple[str, ...] = ()


class ForgeHealth(VersionedContract):
    """§46 engine health over the wire — declared counts, honest state."""

    schema: Literal["apiforge/forge-health/v1"] = "apiforge/forge-health/v1"  # type: ignore[assignment]
    engine: str = Field(min_length=1)
    protocol_version: str = Field(min_length=1)
    state: Literal["ok", "degraded"] = "ok"
    capabilities: int = Field(default=0, ge=0)
    tasks_by_state: Mapping[str, int] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()


__all__ = [
    "ENGINE_NAME",
    "PROTOCOL_VERSION",
    "ForgeCapabilityDescriptor",
    "ForgeEvidenceArtifact",
    "ForgeEvidenceBundle",
    "ForgeHandoff",
    "ForgeHealth",
    "ForgeResultStatus",
    "ForgeTaskRequest",
    "ForgeTaskState",
    "ForgeTaskStatus",
]
