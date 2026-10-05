"""Versioned contracts for OTLP export and real-collector acceptance (§50-§52)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, Sha256


class OtlpExport(VersionedContract):
    """Envelope describing one OTLP ``ExportTraceServiceRequest`` payload.

    ``payload`` is the OTLP/JSON object itself; the envelope records how many
    ledger spans were converted and which could not be represented.
    """

    schema: Literal["apiforge/otlp-export/v1"] = "apiforge/otlp-export/v1"  # type: ignore[assignment]
    service_name: str = Field(min_length=1)
    span_count: int = Field(ge=0)
    payload: JsonValue
    source_sha256: Sha256 | None = None
    unresolved: tuple[str, ...] = ()


class OtlpValidation(VersionedContract):
    """Deterministic structural acceptance of one OTLP/JSON payload.

    This is the offline half of §52 — it checks the exact shape a collector
    requires (resourceSpans → scopeSpans → spans, hex ids, unix-nano
    timestamps, declared ``gen_ai.operation.name``) without a network.
    """

    schema: Literal["apiforge/otlp-validation/v1"] = "apiforge/otlp-validation/v1"  # type: ignore[assignment]
    accepted: bool
    span_count: int = Field(ge=0)
    problems: tuple[str, ...] = ()
    operations: tuple[str, ...] = ()


class CollectorProbe(VersionedContract):
    """§52 the real-collector acceptance record.

    ``accepted`` counts spans found in the collector's declared output file
    after the POST; ``status`` stays ``unresolved`` when no collector or
    output file was reachable — acceptance is never claimed on faith.
    """

    schema: Literal["apiforge/collector-probe/v1"] = "apiforge/collector-probe/v1"  # type: ignore[assignment]
    endpoint: str | None = None
    sent: int = Field(ge=0)
    accepted: int | None = Field(default=None, ge=0)
    status: Literal["accepted", "refused", "unresolved"]
    detail: str = ""
    code: str | None = None
    unresolved: tuple[str, ...] = ()


__all__ = ["CollectorProbe", "OtlpExport", "OtlpValidation"]
