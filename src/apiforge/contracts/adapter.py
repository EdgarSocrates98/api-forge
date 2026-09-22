"""Contracts shared by source, fixture and live API adapters.

An adapter result must make its execution boundary explicit.  A finding
produced from source text is not equivalent to one observed through a live
read-only integration, and neither is equivalent to a verified runtime
observation.  Keeping that distinction in a closed contract prevents later
stages from treating heuristic output as production evidence.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract

AdapterMode = Literal["static", "fixture", "live_read_only", "live_mutation"]
AdapterStatus = Literal["completed", "partial", "blocked", "failed", "inconclusive"]
EvidenceLevel = Literal["observed", "declared", "inferred", "heuristic", "verified", "unknown"]


class AdapterExecution(VersionedContract):
    """Provenance and limits for one adapter execution.

    ``live_mutation`` is represented for policy decisions but is not an
    approval to execute mutations.  The host/policy layer must reject it
    unless an explicit approval evidence exists.
    """

    adapter_id: str
    adapter_version: str = "unknown"
    mode: AdapterMode = "static"
    status: AdapterStatus = "completed"
    evidence_level: EvidenceLevel = "unknown"
    input_hashes: tuple[tuple[str, str], ...] = ()
    tools: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @field_validator("input_hashes", mode="after")
    @classmethod
    def sort_input_hashes(cls, value: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(value))

    @field_validator("tools", "evidence_refs", "unresolved", "limitations", mode="after")
    @classmethod
    def sort_unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class AdapterCapability(VersionedContract):
    """Declared capability of an adapter, never proof that it ran."""

    adapter_id: str
    capability: str
    mode: AdapterMode
    evidence_level: EvidenceLevel
    requires_toolchain: tuple[str, ...] = Field(default_factory=tuple)
    supports_live_data: bool = False
    supports_mutation: bool = False

    @field_validator("requires_toolchain", mode="after")
    @classmethod
    def sort_toolchain(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))
