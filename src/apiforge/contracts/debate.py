"""Contracts for bounded adaptive debates."""

from __future__ import annotations

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel


class AdaptivePolicy(VersionedContract):
    max_participants: int = Field(default=3, ge=2, le=8)
    max_rounds: int = Field(default=2, ge=1, le=8)
    quorum_sides: int = Field(default=2, ge=2, le=8)
    retry_budget: int = Field(default=1, ge=0, le=8)
    preserve_dissent: bool = True
    evidence_level: EvidenceLevel = "declared"


class ParticipantDeclaration(VersionedContract):
    participant_id: str
    host: str
    capabilities: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "declared"

    @field_validator("capabilities", "evidence_refs", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class AdaptivePlan(VersionedContract):
    risk: str
    participants: tuple[ParticipantDeclaration, ...]
    quorum_sides: int
    max_rounds: int
    retry_budget: int
    reason: str
    evidence_level: EvidenceLevel = "declared"


class DebateReplay(VersionedContract):
    replay_id: str
    policy: AdaptivePolicy
    plan: AdaptivePlan
    rounds: tuple[dict[str, object], ...] = ()
    dissent: tuple[dict[str, object], ...] = ()
    evidence_level: EvidenceLevel = "observed"
