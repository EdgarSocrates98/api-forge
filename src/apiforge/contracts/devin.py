"""Versioned payload contracts for the Devin Desktop, CLI and Cloud surfaces."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord

DevinSurface = Literal["desktop", "cli", "cloud"]
DevinTaskKind = Literal[
    "discovery",
    "planning",
    "implementation",
    "verification",
    "review",
    "handoff",
]
DevinPermissionMode = Literal[
    "normal",
    "accept-edits",
    "smart",
    "dangerous",
    "autonomous",
]
DevinPromptTransport = Literal["positional", "prompt-file", "desktop-paste", "slash-command"]


class DevinCheck(VersionedContract):
    """A verification command Devin may run, with its intended proof."""

    name: str
    command: str
    purpose: str
    required: bool = True
    evidence_level: EvidenceLevel = "declared"


class DevinLaunch(VersionedContract):
    """How a payload is handed to a particular Devin surface."""

    surface: DevinSurface
    executable: str = "devin"
    args: tuple[str, ...] = ()
    prompt_transport: DevinPromptTransport = "positional"
    slash_commands: tuple[str, ...] = ()
    operator_steps: tuple[str, ...] = ()

    @field_validator("args", "slash_commands", "operator_steps", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(value)


class DevinPayload(VersionedContract):
    """A portable, non-executing Devin task payload for API Forge."""

    surface: DevinSurface
    task_kind: DevinTaskKind
    title: str
    objective: str
    prompt: str
    working_directory: str = "."
    case_path: str = ".apiforge/case"
    launch: DevinLaunch
    permission_mode: DevinPermissionMode = "normal"
    sandbox: bool = False
    model: str | None = None
    expected_outputs: tuple[str, ...] = ()
    checks: tuple[DevinCheck, ...] = ()
    prohibited_actions: tuple[str, ...] = ()
    requires_human_confirmation: bool = True
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    evidence_level: EvidenceLevel = "declared"

    @field_validator(
        "expected_outputs",
        "prohibited_actions",
        mode="after",
    )
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(value))


class DevinCliProbe(VersionedContract):
    """Read-only local observation of the Devin CLI executable."""

    installed: bool = False
    executable: str | None = None
    cli_version: str | None = None
    error: str | None = None
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    evidence_level: EvidenceLevel = "unknown"


__all__ = [
    "DevinCheck",
    "DevinCliProbe",
    "DevinLaunch",
    "DevinPayload",
    "DevinPermissionMode",
    "DevinPromptTransport",
    "DevinSurface",
    "DevinTaskKind",
]
