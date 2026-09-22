"""Canonical, provider-neutral observability contracts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, freeze_json

SignalKind = Literal["trace", "span", "metric", "log", "event"]
IntentKind = Literal["monitor", "slo", "dashboard", "query", "event"]
Risk = Literal["read_only", "local_reversible", "external_mutation"]
ObservabilityProvider = Literal["otel", "datadog", "dynatrace", "cloudwatch"]


class TelemetryRecord(VersionedContract):
    id: str
    kind: SignalKind
    service: str
    operation: str | None = None
    timestamp: str | None = None
    duration_ms: float | None = None
    status_code: int | None = None
    value: float | None = None
    attributes: Mapping[str, JsonValue] = Field(default_factory=dict)
    source: str = "unknown"
    source_hash: str | None = None

    @field_validator("attributes", mode="after")
    @classmethod
    def freeze_attributes(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("attributes must be an object")
        return frozen


class ObservationSnapshot(VersionedContract):
    snapshot_id: str
    environment: str = "local"
    observed_at: str | None = None
    records: tuple[TelemetryRecord, ...] = ()
    digest: str
    provenance: tuple[str, ...] = ()


class SLODefinition(VersionedContract):
    id: str
    service: str
    objective: float = Field(ge=0, le=1)
    window_seconds: int = Field(gt=0)
    indicator: Literal["availability", "latency"] = "availability"
    threshold_ms: float | None = None


class SignalSummary(VersionedContract):
    service: str
    operation: str | None = None
    request_count: int = Field(ge=0)
    error_count: int = Field(ge=0)
    error_rate: float = Field(ge=0, le=1)
    throughput_tps: float = Field(ge=0)
    p50_ms: float | None = None
    p95_ms: float | None = None
    p99_ms: float | None = None
    cardinality: int = Field(ge=0)
    limitations: tuple[str, ...] = ()


class SLOResult(VersionedContract):
    slo_id: str
    status: Literal["met", "breached", "inconclusive"]
    good_events: int = Field(ge=0)
    total_events: int = Field(ge=0)
    objective: float
    compliance: float | None = None
    error_budget_remaining: float | None = None
    burn_rate: float | None = None
    limitations: tuple[str, ...] = ()


class Capability(VersionedContract):
    name: str
    supported: bool
    read_only: bool = True
    reason: str = ""


class VendorIntent(VersionedContract):
    id: str
    kind: IntentKind
    service: str
    name: str
    specification: Mapping[str, JsonValue] = Field(default_factory=dict)
    risk: Risk = "read_only"
    requires_approval: bool = False

    @field_validator("specification", mode="after")
    @classmethod
    def freeze_specification(cls, value: object) -> JsonValue:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("specification must be an object")
        return frozen


class IntentDiff(VersionedContract):
    intent_id: str
    action: Literal["create", "update", "delete", "unchanged"]
    changes: tuple[str, ...] = ()
    risk: Risk = "read_only"
    requires_approval: bool = False


class OperationReceipt(VersionedContract):
    operation_id: str
    intent_id: str | None = None
    status: Literal["planned", "dry_run", "applied", "verified", "refused", "rolled_back"]
    provider: str
    evidence: tuple[str, ...] = ()
    reason: str = ""


class ReadQuery(VersionedContract):
    provider: ObservabilityProvider
    service: str
    environment: str = "unknown"
    start: str
    end: str
    signals: tuple[Literal["traces", "metrics", "logs", "events"], ...] = ("traces", "metrics")


class ReadPlan(VersionedContract):
    provider: ObservabilityProvider
    query: ReadQuery
    method: Literal["GET"] = "GET"
    endpoint: str
    read_only: bool = True
    network_allowed: bool = False
    credential_required: bool = True
    execution_mode: Literal["fixture_only", "provider_read"] = "fixture_only"
    limitations: tuple[str, ...] = ()


class ObservabilityFinding(VersionedContract):
    id: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    title: str
    detail: str
    evidence: tuple[str, ...] = ()
    status: Literal["confirmed", "recommendation", "inconclusive"] = "recommendation"
