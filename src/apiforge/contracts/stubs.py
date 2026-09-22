"""Stub contracts — version + identity + provenance + unresolved surface.

These are declared now so consumers bind to a real contract early; their
operational shape lands with the layer that produces them (telemetry,
performance runs, data access, runtime matrices). Fields only grow.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, freeze_json

TEST_KINDS = (
    "smoke",
    "baseline",
    "load",
    "stress",
    "spike",
    "soak",
    "capacity",
    "failover",
    "chaos",
)

TestKind = Literal[
    "smoke",
    "baseline",
    "load",
    "stress",
    "spike",
    "soak",
    "capacity",
    "failover",
    "chaos",
]

# FASE 6 — the full risk-based test strategy taxonomy. PerformanceRun keeps
# the 9 perf kinds above; TestRecord spans the whole strategy.
TEST_TAXONOMY = (
    "lint",
    "typecheck",
    "unit",
    "component",
    "integration",
    "contract",
    "consumer_contract",
    "e2e",
    "property",
    "fuzz",
    "mutation",
    "security",
    "load",
    "stress",
    "spike",
    "soak",
    "capacity",
    "failover",
    "chaos",
    "recovery",
    "cost",
)

TEST_STATES = (
    "passed",
    "failed",
    "inconclusive",
    "blocked",
    "skipped_with_reason",
    "unsafe_to_run",
    "not_applicable",
)


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
    """A measured load/performance run.

    Every metric is optional: ``None`` is *measured absence* — the run did
    not report the value — never a zero. ``test_kind`` is a closed
    vocabulary declared by the run's author, never inferred from the
    numbers. TPS fields mean *completed business transactions*; the run
    declares ``tps_completed_transactions`` when its TPS metric provably
    counts completed transactions rather than raw requests.
    """

    subject: str = ""
    duration_ms: float | None = None
    baseline_ref: str | None = None
    test_kind: TestKind | None = None
    # throughput — RPS (requests) and TPS (business transactions) are distinct
    target_tps: float | None = None
    achieved_tps: float | None = None
    successful_tps: float | None = None
    failed_tps: float | None = None
    rps_received: float | None = None
    rps_processed: float | None = None
    tps_completed_transactions: bool | None = None
    # latency
    p50_ms: float | None = None
    p95_ms: float | None = None
    p99_ms: float | None = None
    max_latency_ms: float | None = None
    # error surface
    error_rate: float | None = None
    http_4xx_rate: float | None = None
    http_5xx_rate: float | None = None
    http_429_rate: float | None = None
    timeout_rate: float | None = None
    duplicates_detected: bool | None = None
    # resource / downstream observation
    cpu_percent: float | None = None
    memory_percent: float | None = None
    gc_pause_ms: float | None = None
    connection_pool_usage: float | None = None
    database_latency_ms: float | None = None
    cache_hit_rate: float | None = None
    queue_lag: float | None = None
    consumer_lag: float | None = None
    cold_starts: float | None = None
    cost_per_transaction: float | None = None
    # run provenance
    test_duration_s: float | None = None
    warmup_duration_s: float | None = None
    min_duration_s: float | None = None
    ramp_profile: str | None = None
    payload_profile: str | None = None
    environment: str | None = None
    commit_sha: str | None = None
    infrastructure_revision: str | None = None
    downstreams_observed: bool | None = None
    generator_dropped_iterations: int | None = None
    # declared SLO thresholds the verdict evaluates against
    slo_error_rate: float | None = None
    slo_p99_ms: float | None = None


class CapacityAssessment(_StubPayload):
    """Capacity gate derived from one measured ``PerformanceRun``.

    ``max_safe_tps`` is a declared planning envelope, not a new measurement:
    it is computed only when the run passes and a headroom policy is supplied.
    Missing or invalid evidence remains ``inconclusive``.
    """

    subject: str = ""
    source_run_id: str
    status: Literal["passed", "failed", "inconclusive"]
    target_tps: float | None = None
    achieved_tps: float | None = None
    max_safe_tps: float | None = None
    headroom_pct: float | None = None
    blockers: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


class WorkloadProfile(_StubPayload):
    """Declared workload shape for architecture comparison.

    Every dimension is declared by the plan's author — the profile is a
    planning artifact, never inferred from telemetry. Absent dimensions
    stay ``None`` and are named, not defaulted.
    """

    subject: str = ""
    timing: Literal["synchronous", "asynchronous"] | None = None
    arrival: Literal["bursty", "steady"] | None = None
    state: Literal["stateless", "stateful"] | None = None
    bound: Literal["cpu", "io"] | None = None
    latency_sensitive: bool | None = None
    throughput_sensitive: bool | None = None
    event_driven: bool | None = None
    batch: bool | None = None
    streaming: bool | None = None
    multi_tenant: bool | None = None
    scope: Literal["regional", "global"] | None = None
    exposure: Literal["public", "private"] | None = None
    # decision inputs for the architecture engine — all declared, all optional;
    # absent means the constraint does not participate, never a default
    max_request_duration_s: float | None = None
    max_payload_bytes: int | None = None
    needs_os_control: bool | None = None
    needs_kubernetes: bool | None = None
    team_maturity: Literal["low", "medium", "high"] | None = None
    data_model: Literal["key-value", "document", "graph", "relational", "cache"] | None = None


class DataAccessIR(_StubPayload):
    """Data-access intermediate representation; per-database fields land
    with the database adapters."""

    database: str = ""
    provider: str = ""
    entities: tuple[str, ...] = ()
    access_patterns: tuple[str, ...] = ()


class StreamingAccessIR(_StubPayload):
    """Intermediate representation for Kafka/MSK and streaming clients."""

    broker: Literal["kafka", "msk", "kinesis", "rabbitmq", "nats", "pulsar"]
    provider: str = ""
    topics: tuple[str, ...] = ()
    consumer_groups: tuple[str, ...] = ()
    roles: tuple[Literal["producer", "consumer", "admin"], ...] = ()
    operations: tuple[str, ...] = ()
    delivery_signals: tuple[str, ...] = ()


class MessagingAccessIR(_StubPayload):
    """Intermediate representation for queues, topics, buses and streams."""

    service: Literal["sqs", "sns", "eventbridge", "kinesis"]
    provider: str = "aws"
    destinations: tuple[str, ...] = ()
    roles: tuple[Literal["producer", "consumer", "router"], ...] = ()
    operations: tuple[str, ...] = ()
    reliability_signals: tuple[str, ...] = ()


class DataPerformanceProfile(_StubPayload):
    """Observed low-latency/partitioned datastore signals."""

    database: Literal["redis", "dynamo", "mongo", "neptune"]
    latency_class: Literal["low_latency", "partitioned_scale", "document", "graph", "unknown"]
    observed_signals: tuple[str, ...] = ()
    risk_findings: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class AnalyticalAccessIR(_StubPayload):
    """Intermediate representation for OpenSearch and Redshift access."""

    engine: Literal["opensearch", "redshift"]
    provider: str = ""
    indexes_or_tables: tuple[str, ...] = ()
    operations: tuple[str, ...] = ()
    query_signals: tuple[str, ...] = ()
    risk_findings: tuple[str, ...] = ()


class DataAccessReadiness(_StubPayload):
    """Governance preflight for Redis, MongoDB, DynamoDB and Neptune access."""

    database: Literal["redis", "mongo", "dynamo", "neptune"]
    status: Literal["ready", "review", "blocked"]
    observed_patterns: tuple[str, ...] = ()
    mutation_patterns: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


class ApiSafetyAssessment(_StubPayload):
    """Required API security and resilience controls, evaluated explicitly."""

    subject: str = ""
    status: Literal["ready", "review", "blocked"]
    required_controls: tuple[str, ...] = ()
    passed_controls: tuple[str, ...] = ()
    missing_controls: tuple[str, ...] = ()
    failed_controls: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


class AgenticQualityAssessment(_StubPayload):
    """Aggregate golden/holdout eval and host-parity readiness."""

    subject: str = ""
    status: Literal["ready", "review", "blocked"]
    total_cases: int = Field(ge=0)
    passed_cases: int = Field(ge=0)
    review_cases: int = Field(ge=0)
    blocked_cases: int = Field(ge=0)
    holdout_covered: int = Field(ge=0)
    host_gaps: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


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


class TestRecord(_StubPayload):
    """One executed test in the risk-based strategy (FASE 6).

    ``state`` is a closed 7-value vocabulary — a record is never "passed
    by absence of error": ``passed`` requires the run to have produced
    its declared metric. Every field is optional; ``None``/empty means
    not recorded, never zero.
    """

    kind: (
        Literal[
            "lint",
            "typecheck",
            "unit",
            "component",
            "integration",
            "contract",
            "consumer_contract",
            "e2e",
            "property",
            "fuzz",
            "mutation",
            "security",
            "load",
            "stress",
            "spike",
            "soak",
            "capacity",
            "failover",
            "chaos",
            "recovery",
            "cost",
        ]
        | None
    ) = None
    state: (
        Literal[
            "passed",
            "failed",
            "inconclusive",
            "blocked",
            "skipped_with_reason",
            "unsafe_to_run",
            "not_applicable",
        ]
        | None
    ) = None
    objective: str | None = None
    scenario: str | None = None
    inputs: tuple[str, ...] = ()
    environment: str | None = None
    tool: str | None = None
    tool_version: str | None = None
    duration_s: float | None = None
    data_used: str | None = None
    metric: str | None = None
    threshold: str | None = None
    evidence: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    reproducible: bool | None = None
    reason: str | None = None
