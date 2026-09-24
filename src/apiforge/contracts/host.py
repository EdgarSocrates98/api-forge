"""Host-neutral capability declarations and negotiation results."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord

HostName = Literal["claude", "gpt-codex", "devin", "copilot"]
SupportState = Literal["supported", "unsupported", "unresolved", "degraded"]


class HostCapability(VersionedContract):
    capability: str
    state: SupportState = "unresolved"
    prerequisites: tuple[str, ...] = ()
    limits: tuple[str, ...] = ()
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    evidence_level: EvidenceLevel = "declared"

    @field_validator("prerequisites", "limits", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class HostDeclaration(VersionedContract):
    host: HostName
    adapter_version: str = "unknown"
    capabilities: tuple[HostCapability, ...] = ()
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    evidence_level: EvidenceLevel = "declared"


class HostCapabilityRequest(VersionedContract):
    capability: str
    hosts: tuple[HostName, ...] = ("claude", "gpt-codex", "devin", "copilot")
    required_prerequisites: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "declared"


class HostResolution(VersionedContract):
    capability: str
    eligible_hosts: tuple[HostName, ...] = ()
    excluded_hosts: tuple[HostName, ...] = ()
    limitations: tuple[str, ...] = ()
    evidence: tuple[EvidenceRecord, ...] = ()
    next_action: str = "review"
    evidence_level: EvidenceLevel = "unknown"
