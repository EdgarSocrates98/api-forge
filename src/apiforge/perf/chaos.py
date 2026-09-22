"""Controlled failure-injection scenarios — FASE 12.

Declared data, not executable recipes: each scenario names the fault to
inject, the signal that proves the system absorbed it, the blast-radius
guard, and the evidence a run must produce. API Forge never injects the
fault itself — execution belongs to the environment's own chaos tooling.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChaosScenario:
    id: str
    name: str
    injection: str
    expected_signal: str
    blast_radius: str
    evidence_required: str


SCENARIOS: tuple[ChaosScenario, ...] = (
    ChaosScenario(
        id="CHAOS-001",
        name="total dependency outage",
        injection="blackhole all traffic to one declared dependency",
        expected_signal="circuit opens; callers fail fast within their timeout; no pool exhaustion",
        blast_radius="single dependency, single environment, traffic-capped",
        evidence_required="latency + error-rate metrics during injection, breaker state transitions",
    ),
    ChaosScenario(
        id="CHAOS-002",
        name="gradual dependency latency",
        injection="add latency ramping 50ms→2s to one dependency",
        expected_signal="p95 rises but stays under SLO; no thread/connection starvation",
        blast_radius="one dependency, capped injection window",
        evidence_required="latency percentiles over the ramp, pool occupancy",
    ),
    ChaosScenario(
        id="CHAOS-003",
        name="extreme dependency latency",
        injection="add 30s latency to one dependency",
        expected_signal="callers time out at their declared timeout, never later",
        blast_radius="one dependency, capped injection window",
        evidence_required="timeout count, max observed wait vs declared timeout",
    ),
    ChaosScenario(
        id="CHAOS-004",
        name="random timeouts",
        injection="drop a random fraction of dependency responses",
        expected_signal="retries absorb transient loss or surface a bounded error",
        blast_radius="one dependency, loss fraction declared upfront",
        evidence_required="retry count, error rate, eventual success rate",
    ),
    ChaosScenario(
        id="CHAOS-005",
        name="intermittent failures",
        injection="alternate 5xx and success on one dependency",
        expected_signal="breaker flaps or retries succeed; no silent corruption",
        blast_radius="one dependency",
        evidence_required="state transitions, error budget burn during injection",
    ),
    ChaosScenario(
        id="CHAOS-006",
        name="partial traffic loss",
        injection="drop a declared percentage of requests at the edge",
        expected_signal="lost requests are retried by clients or surfaced — never silently doubled",
        blast_radius="edge only, percentage declared upfront",
        evidence_required="request counts client vs server, duplicate rate",
    ),
    ChaosScenario(
        id="CHAOS-007",
        name="queue saturation",
        injection="pause consumers until the queue reaches a declared depth",
        expected_signal="backpressure or DLQ routing engages; producers are bounded",
        blast_radius="one queue, depth cap declared upfront",
        evidence_required="queue depth, oldest message age, DLQ arrivals",
    ),
    ChaosScenario(
        id="CHAOS-008",
        name="database saturation",
        injection="cap database connections/CPU at a declared level",
        expected_signal="pool waits bounded; graceful degradation or explicit 503s",
        blast_radius="one datastore, capacity cap declared upfront",
        evidence_required="pool wait time, rejected-request count, recovery time",
    ),
    ChaosScenario(
        id="CHAOS-009",
        name="extreme concurrency",
        injection="hold requests open to exhaust the worker pool",
        expected_signal="bounded concurrency refuses excess fast; no deadlock",
        blast_radius="single instance",
        evidence_required="active connections, refusal rate, recovery after release",
    ),
    ChaosScenario(
        id="CHAOS-010",
        name="partial event loss",
        injection="drop a declared fraction of published events",
        expected_signal="consumers detect the gap (sequence/ack) or reconciliation catches it",
        blast_radius="one topic/stream, fraction declared upfront",
        evidence_required="published vs consumed counts, gap-detection evidence",
    ),
    ChaosScenario(
        id="CHAOS-011",
        name="event duplication",
        injection="deliver each event twice to consumers",
        expected_signal="idempotent consumers apply once — dedup evidence required",
        blast_radius="one consumer group",
        evidence_required="duplicate delivery count, mutation count after dedup",
    ),
    ChaosScenario(
        id="CHAOS-012",
        name="out-of-order events",
        injection="shuffle event order within a declared window",
        expected_signal="consumers reorder or reject per declared ordering contract",
        blast_radius="one consumer group, window declared upfront",
        evidence_required="order violations observed, consumer handling decisions",
    ),
    ChaosScenario(
        id="CHAOS-013",
        name="abrupt shutdown mid-operation",
        injection="kill the process during a declared write path",
        expected_signal="recovery completes or rolls back — never a partial write",
        blast_radius="single instance, state inspected after restart",
        evidence_required="post-restart state check, in-flight operation outcome",
    ),
)


def list_scenarios() -> list[dict[str, str]]:
    return [
        {
            "id": s.id,
            "name": s.name,
            "injection": s.injection,
            "expected_signal": s.expected_signal,
            "blast_radius": s.blast_radius,
            "evidence_required": s.evidence_required,
        }
        for s in SCENARIOS
    ]
