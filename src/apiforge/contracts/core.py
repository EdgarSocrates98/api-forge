"""Core lifecycle contracts: ArtifactRef, Decision, ActionPlan, Verification."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel
from apiforge.core.models import JsonValue, Sha256, freeze_json


class ArtifactRef(VersionedContract):
    """Pointer to a content-addressed artifact — path + sha256, never inline."""

    path: str
    sha256: Sha256
    kind: str = "file"
    evidence_level: EvidenceLevel = "unknown"


class DecisionStatus(StrEnum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class Decision(VersionedContract):
    """A recorded decision: what was chosen, by whom, on which evidence."""

    id: str
    summary: str
    status: DecisionStatus = DecisionStatus.PROPOSED
    decided_by: str | None = None
    evidence: tuple[str, ...] = ()
    supersedes: str | None = None
    rationale: str = ""
    evidence_level: EvidenceLevel = "unknown"


class ActionRisk(StrEnum):
    READ_ONLY = "read_only"
    LOCAL_REVERSIBLE = "local_reversible"
    SENSITIVE = "sensitive"
    EXTERNAL_MUTATION = "external_mutation"
    DESTRUCTIVE = "destructive"
    IRREVERSIBLE = "irreversible"


class ActionStep(VersionedContract):
    verb: str
    args: Mapping[str, JsonValue] = Field(default_factory=dict)
    proposed_diff: str | None = None

    @field_validator("args", mode="after")
    @classmethod
    def freeze_args(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("step args must be a JSON object")  # noqa: TRY004
        return frozen


class ActionPlan(VersionedContract):
    """A proposed sequence of verbs — a suggestion, never auto-applied."""

    id: str
    steps: tuple[ActionStep, ...]
    risk: ActionRisk = ActionRisk.READ_ONLY
    rollback: str = ""
    requires_approval: bool = False
    status: Literal["proposed", "authorized", "executed", "refused"] = "proposed"
    reason: str = ""
    evidence_level: EvidenceLevel = "unknown"


class VerificationResult(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNRESOLVED = "unresolved"


class Verification(VersionedContract):
    """A check over a subject — method, result, evidence. Never implicit."""

    id: str
    subject: str
    method: str
    result: VerificationResult = VerificationResult.UNRESOLVED
    evidence: tuple[str, ...] = ()
    verified_by: str = "apiforge"
    evidence_level: EvidenceLevel = "unknown"
