"""Provider circuit events, metrics and deterministic alert projections."""

from __future__ import annotations

from collections.abc import Iterable

from apiforge.contracts.observability import (
    CircuitBreakerEvent,
    CircuitBreakerMetrics,
    ObservabilityProvider,
)


class InMemoryCircuitEventSink:
    def __init__(self) -> None:
        self.events: list[CircuitBreakerEvent] = []

    def emit(self, event: CircuitBreakerEvent) -> None:
        self.events.append(event)


def metrics_for_provider(
    provider: ObservabilityProvider,
    events: Iterable[CircuitBreakerEvent],
    state: str,
) -> CircuitBreakerMetrics:
    selected = tuple(event for event in events if event.provider == provider)
    openings = sum(event.kind == "opened" for event in selected)
    blocked = sum(event.kind == "blocked" for event in selected)
    failures = sum(event.kind == "failure" for event in selected)
    recoveries = sum(event.kind == "recovered" for event in selected)
    alerts: list[str] = []
    if openings:
        alerts.append(f"provider_circuit_open:{provider}")
    if blocked:
        alerts.append(f"provider_circuit_blocked:{provider}")
    return CircuitBreakerMetrics(
        provider=provider,
        failures=failures,
        openings=openings,
        blocked_calls=blocked,
        recoveries=recoveries,
        state=state,  # type: ignore[arg-type]
        alerts=tuple(alerts),
    )
