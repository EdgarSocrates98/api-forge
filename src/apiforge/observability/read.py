"""Read-only provider query plans; live execution is an explicit future adapter."""

from __future__ import annotations

from typing import Literal

from apiforge.contracts.observability import ObservabilityProvider, ReadPlan, ReadQuery

_ENDPOINTS: dict[ObservabilityProvider, str] = {
    "otel": "local://otel-export",
    "datadog": "https://api.datadoghq.com/api/v2/apm/traces",
    "dynatrace": "https://{environment-id}.live.dynatrace.com/api/v2/metrics/query",
    "cloudwatch": "https://monitoring.{region}.amazonaws.com/",
}


def build_read_plan(
    provider: str,
    service: str,
    start: str,
    end: str,
    *,
    environment: str = "unknown",
    signals: tuple[Literal["traces", "metrics", "logs", "events"], ...] = ("traces", "metrics"),
) -> ReadPlan:
    if provider not in _ENDPOINTS:
        raise ValueError(f"AF-OBS-READ-PROVIDER: unsupported provider {provider!r}")
    selected = provider
    endpoint = _ENDPOINTS[selected]
    limitations = (
        "fixture_only until a credential broker and provider adapter are explicitly configured",
        "query is read-only; no dashboard, monitor or SLO mutation is permitted",
    )
    return ReadPlan(
        provider=selected,
        query=ReadQuery(
            provider=selected,
            service=service,
            environment=environment,
            start=start,
            end=end,
            signals=signals,
        ),
        endpoint=endpoint,
        limitations=limitations,
    )


def fixture_receipt(plan: ReadPlan, record_count: int) -> dict[str, object]:
    """Record a local fixture read without claiming that a provider was queried."""
    if record_count < 0:
        raise ValueError("AF-OBS-READ-COUNT: record_count must be non-negative")
    return {
        "provider": plan.provider,
        "status": "fixture_only",
        "record_count": record_count,
        "network_called": False,
        "credential_used": False,
        "evidence": ("read-plan", "local-fixture", "network_called:false"),
    }
