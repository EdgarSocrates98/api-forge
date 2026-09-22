"""RED/USE-style deterministic signal summaries."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from apiforge.contracts.observability import SignalSummary, TelemetryRecord
from apiforge.observability.redaction import cardinality


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * percentile)))
    return ordered[index]


def summarize(records: Iterable[TelemetryRecord], duration_seconds: float | None = None) -> tuple[SignalSummary, ...]:
    groups: dict[tuple[str, str | None], list[TelemetryRecord]] = defaultdict(list)
    for record in records:
        if record.kind in ("span", "trace"):
            groups[(record.service, record.operation)].append(record)
    result: list[SignalSummary] = []
    for (service, operation), group in sorted(groups.items()):
        durations = [r.duration_ms for r in group if r.duration_ms is not None]
        errors = sum(1 for r in group if r.status_code is not None and r.status_code >= 500)
        seconds = duration_seconds or 1.0
        result.append(SignalSummary(
            service=service,
            operation=operation,
            request_count=len(group),
            error_count=errors,
            error_rate=errors / len(group) if group else 0,
            throughput_tps=len(group) / seconds,
            p50_ms=_percentile(durations, 0.5),
            p95_ms=_percentile(durations, 0.95),
            p99_ms=_percentile(durations, 0.99),
            cardinality=sum(cardinality(r.attributes) for r in group),
            limitations=("duration missing",) if not durations else (),
        ))
    return tuple(result)
