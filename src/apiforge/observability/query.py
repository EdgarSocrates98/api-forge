"""Provider-specific encoding for read-only observability queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from apiforge.contracts.observability import ReadPlan

if TYPE_CHECKING:
    from collections.abc import Mapping


def build_provider_params(plan: ReadPlan) -> Mapping[str, str]:
    """Encode a canonical plan without adding credentials or network behavior."""
    query = plan.query
    signals = ",".join(query.signals)
    common = {"start": query.start, "end": query.end, "signals": signals}
    if query.provider == "datadog":
        return {
            "service": query.service,
            "environment": query.environment,
            "filter[query]": f"service:{query.service}",
            "filter[from]": query.start,
            "filter[to]": query.end,
            "env": query.environment,
            "signals": signals,
        }
    if query.provider == "dynatrace":
        return {
            "service": query.service,
            "entitySelector": f"type(SERVICE),entityName.equals({query.service})",
            "from": query.start,
            "to": query.end,
            "metricSelector": signals,
            "environment": query.environment,
        }
    if query.provider == "cloudwatch":
        return {
            "service": query.service,
            "Namespace": query.service,
            "StartTime": query.start,
            "EndTime": query.end,
            "MetricNames": signals,
            "Environment": query.environment,
        }
    return {"service.name": query.service, "environment": query.environment, **common}
