"""Stub contracts — version + identity + provenance + unresolved surface.

These are declared now so consumers bind to a real contract early; their
operational shape lands with the layer that produces them (telemetry,
performance runs, data access, runtime matrices). Fields only grow.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, freeze_json


class _StubPayload(VersionedContract):
    """Shared stub shape: identity, provenance, unresolved surface."""

    id: str
    produced_by: str = "apiforge"
    unresolved: tuple[str, ...] = ()
    attributes: Mapping[str, JsonValue] = Field(default_factory=dict)

    @field_validator("attributes", mode="after")
    @classmethod
    def freeze_attrs(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("attributes must be a JSON object")  # noqa: TRY004
        return frozen


class TelemetryEvent(_StubPayload):
    """OTel-shaped event; full span/metric fields land with the telemetry layer."""

    name: str = ""
    observed_at: str | None = None


class PerformanceRun(_StubPayload):
    """A measured run; metrics and noise-floor fields land with perf layer."""

    subject: str = ""
    duration_ms: float | None = None
    baseline_ref: str | None = None


class DataAccessIR(_StubPayload):
    """Data-access intermediate representation; per-database fields land
    with the database adapters."""

    database: str = ""
    provider: str = ""
    entities: tuple[str, ...] = ()
    access_patterns: tuple[str, ...] = ()


class RuntimeMatrix(_StubPayload):
    """Versioned runtime constraints; entries land with each knowledge pack."""

    subject: str = ""
    verified_on: str | None = None
    constraints: Mapping[str, JsonValue] = Field(default_factory=dict)

    @field_validator("constraints", mode="after")
    @classmethod
    def freeze_constraints(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise ValueError("constraints must be a JSON object")  # noqa: TRY004
        return frozen
