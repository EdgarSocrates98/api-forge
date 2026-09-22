"""Noise-floor measurement over repeated PerformanceRun payloads.

The floor is a *measured* property of the environment: ``(max - min) /
mean`` across repeated runs of the same subject for one metric. With fewer
than two observations there is no floor — the measure returns ``None`` and
callers name the floor *unproven* rather than assuming a constant. A
zero-mean signal with any spread has no meaningful relative floor either.

Two surfaces consume it: run-level fields (``error_rate``, ``p99_ms`` …)
for ``perf verdict``, and per-operation metrics (``mean_ms``, ``p95_ms`` …)
for ``perf compare``.
"""

from __future__ import annotations

from typing import Any

from apiforge.contracts.stubs import PerformanceRun

# Run-level numeric fields a baseline comparison can be judged on.
RUN_FIELDS: tuple[str, ...] = (
    "error_rate",
    "p99_ms",
    "p95_ms",
    "achieved_tps",
    "rps_processed",
)


def noise_floor(values: list[float]) -> float | None:
    """``(max - min) / mean`` over ≥2 observations; ``None`` when unproven."""
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0 if max(values) == min(values) else None
    return (max(values) - min(values)) / abs(mean)


def field_noise(runs: list[PerformanceRun], field: str) -> dict[str, Any]:
    """Floor over a run-level field across repeated runs."""
    values = [float(v) for r in runs if isinstance((v := getattr(r, field, None)), (int, float))]
    return {"field": field, "floor": noise_floor(values), "n": len(values)}


def metric_noise(runs: list[PerformanceRun], metric: str) -> dict[str, Any]:
    """Floor over a per-operation metric pooled across repeated runs."""
    values: list[float] = []
    for run in runs:
        ops = run.attributes.get("operations")
        if not isinstance(ops, dict):
            continue
        for op in ops.values():
            if isinstance(op, dict) and isinstance((v := op.get(metric)), (int, float)):
                values.append(float(v))
    return {"metric": metric, "floor": noise_floor(values), "n": len(values)}


def noise_report(
    runs: list[PerformanceRun],
    *,
    fields: tuple[str, ...] = RUN_FIELDS,
    metrics: tuple[str, ...] = ("mean_ms", "p95_ms"),
) -> dict[str, Any]:
    """Declared fields + operation metrics -> measured floors and counts."""
    return {
        "runs": len(runs),
        "fields": {f: field_noise(runs, f) for f in fields},
        "metrics": {m: metric_noise(runs, m) for m in metrics},
    }
