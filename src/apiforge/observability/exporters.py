"""Optional, callback-driven circuit metrics exporters."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Literal

from apiforge.contracts.observability import (
    CircuitBreakerMetrics,
    CircuitMetricsExportReceipt,
)

ExportBackend = Literal["otel", "datadog", "dynatrace"]
Payload = Mapping[str, object]
PayloadSender = Callable[[Payload], None]


def _points(metrics: CircuitBreakerMetrics) -> list[dict[str, object]]:
    prefix = "api_forge.circuit"
    values = {
        "failures": metrics.failures,
        "openings": metrics.openings,
        "blocked_calls": metrics.blocked_calls,
        "recoveries": metrics.recoveries,
    }
    return [
        {"name": f"{prefix}.{name}", "value": value, "provider": metrics.provider}
        for name, value in values.items()
    ]


def build_export_payload(backend: ExportBackend, metrics: CircuitBreakerMetrics) -> Payload:
    points = _points(metrics)
    if backend == "otel":
        return {
            "resourceMetrics": [
                {
                    "resource": {"attributes": [{"key": "service.name", "value": "api-forge"}]},
                    "scopeMetrics": [{"metrics": points}],
                }
            ]
        }
    if backend == "datadog":
        return {
            "series": [
                {
                    "metric": point["name"],
                    "type": "count",
                    "points": [[0, point["value"]]],
                    "tags": [f"provider:{metrics.provider}", f"state:{metrics.state}"],
                }
                for point in points
            ]
        }
    return {
        "gauge": [
            {
                "metricId": point["name"],
                "value": point["value"],
                "dimensions": {"provider": metrics.provider, "state": metrics.state},
            }
            for point in points
        ]
    }


def export_metrics(
    backend: ExportBackend,
    metrics: CircuitBreakerMetrics,
    sender: PayloadSender | None = None,
) -> CircuitMetricsExportReceipt:
    if sender is None:
        return CircuitMetricsExportReceipt(
            provider=metrics.provider,
            backend=backend,
            status="disabled",
            metric_count=4,
            evidence=("exporter-disabled", "network_called:false"),
        )
    payload = build_export_payload(backend, metrics)
    try:
        sender(payload)
    except (OSError, RuntimeError, TimeoutError) as exc:
        return CircuitMetricsExportReceipt(
            provider=metrics.provider,
            backend=backend,
            status="failed",
            metric_count=4,
            network_called=True,
            evidence=(f"export-error:{type(exc).__name__}", "network_called:true"),
        )
    return CircuitMetricsExportReceipt(
        provider=metrics.provider,
        backend=backend,
        status="sent",
        metric_count=4,
        network_called=True,
        evidence=("callback-injected", "network_called:true"),
    )
