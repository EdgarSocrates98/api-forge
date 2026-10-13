"""Closed contracts for safe local sandbox command execution."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract


class SandboxCommand(VersionedContract):
    command: tuple[str, ...] = Field(min_length=1)
    cwd: str
    timeout_seconds: int = Field(default=120, ge=1, le=3600)
    network: Literal["disabled", "inherited"] = "disabled"
    environment: tuple[tuple[str, str], ...] = ()


class SandboxCommandResult(VersionedContract):
    status: Literal["passed", "failed", "timed_out", "blocked", "inconclusive"]
    command: tuple[str, ...]
    cwd: str
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_ms: int | None = None
    evidence_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
