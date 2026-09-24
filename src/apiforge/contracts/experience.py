"""Stable, read-only view contracts shared by CLI, Rich, JSON and TUI."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceRecord

ExperienceStatus = Literal["READY", "RUNNING", "DONE", "REVIEW", "BLOCKED", "UNRESOLVED"]


class ExperienceView(VersionedContract):
    """Canonical projection; presentation layers must not add semantics."""

    task_id: str
    status: ExperienceStatus = "REVIEW"
    title: str = "API Forge"
    summary: str = ""
    gaps: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    payload: dict[str, object] = Field(default_factory=dict)
    evidence_level: Literal[
        "observed", "declared", "inferred", "heuristic", "verified", "unknown"
    ] = "unknown"

    @field_validator("gaps", "actions", "evidence_refs", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class ExperienceAction(VersionedContract):
    """A named action a surface may offer; execution stays in application services."""

    name: str
    label: str
    safe: bool = True
    requires_confirmation: bool = False
    evidence_level: Literal[
        "observed", "declared", "inferred", "heuristic", "verified", "unknown"
    ] = "declared"


class ExperienceSnapshot(VersionedContract):
    """Projection bundle used by parity tests and headless renderers."""

    view: ExperienceView
    actions: tuple[ExperienceAction, ...] = ()
    surface: str = "json"
    evidence_level: Literal[
        "observed", "declared", "inferred", "heuristic", "verified", "unknown"
    ] = "unknown"
