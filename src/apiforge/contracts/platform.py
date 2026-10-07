"""Contracts for public platform capabilities and surface parity."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, freeze_json

CapabilityState = Literal["supported", "heuristic", "unresolved", "unsupported"]
CapabilityRisk = Literal["read_only", "local_reversible", "sensitive", "external_mutation"]
SurfaceName = Literal["cli", "mcp", "ide", "ui"]
RequestAction = Literal["inspect", "plan", "apply", "verify"]
ResultStatus = Literal["ok", "review", "blocked", "failed"]


class CapabilityRecord(VersionedContract):
    """Machine-readable public capability promise and its proof boundary."""

    capability_id: str
    vertical: str
    operation: str
    state: CapabilityState
    surfaces: tuple[SurfaceName, ...] = ()
    evidence: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    risk: CapabilityRisk = "read_only"
    rollback: str
    verifier: str
    documentation: str
    adapter: str | None = None

    @field_validator(
        "surfaces",
        "evidence",
        "limitations",
        "prerequisites",
        mode="after",
    )
    @classmethod
    def unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class CapabilityRequest(VersionedContract):
    """Canonical request shared by CLI, MCP, IDE and UI projections."""

    capability_id: str
    intent: str
    surface: SurfaceName
    action: RequestAction = "inspect"
    context: Mapping[str, JsonValue] = Field(default_factory=dict)
    case_id: str | None = None
    detail_level: Literal["summary", "normal", "full"] = "normal"

    @field_validator("context", mode="after")
    @classmethod
    def freeze_context(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("context must be a JSON object")
        return frozen


class CapabilityResult(VersionedContract):
    """Canonical result projection; presentation layers must not reinterpret it."""

    capability_id: str
    state: CapabilityState
    status: ResultStatus
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

    @field_validator("evidence", "gaps", "limitations", mode="after")
    @classmethod
    def unique_result_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))


class VerticalCoverage(VersionedContract):
    """One fixture, golden and holdout declaration for a vertical."""

    vertical: str
    fixture: str
    golden: str
    holdout: str
    verifier: str


class VerticalRuntimeReceipt(VersionedContract):
    """Receipt for one allowlisted local runtime probe."""

    vertical: str
    fixture: str
    probe: str
    probe_sha256: str
    observed_at: str
    status: Literal["passed", "failed", "unresolved"]
    checks: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()


class PlatformRuntimeReceipt(VersionedContract):
    """Aggregate local runtime evidence for the six required verticals."""

    schema_version: Literal["af-platform-runtime-receipt/1"] = "af-platform-runtime-receipt/1"
    observed_at: str
    verticals: tuple[VerticalRuntimeReceipt, ...] = ()
    limitations: tuple[str, ...] = (
        "probes prove the committed local fixture runtime only",
        "provider freshness, deployment safety and production SLOs require external receipts",
    )
