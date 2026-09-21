"""Deterministic comparison of two PerformanceRun payloads.

``compare_runs`` pairs operations present in both runs and reports
deltas for ``mean_ms``/``p95_ms``; ``detect_regression`` flags deltas
above a caller-supplied threshold. Operations present on only one side
are named as ``added``/``removed``, never silently dropped; operations
below the minimum sample count are named ``insufficient_data`` rather
than judged. The threshold is an explicit argument — never a default
buried in the catalog.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from apiforge.contracts.stubs import PerformanceRun


class Regression(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    operation: str
    metric: str
    baseline_ms: float
    candidate_ms: float
    delta_pct: float


class ComparisonReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    baseline_ref: str
    candidate_ref: str
    threshold_pct: float
    min_samples: int
    regressions: tuple[Regression, ...] = ()
    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    insufficient_data: tuple[str, ...] = ()
    compared: int = 0


def _ops(run: PerformanceRun) -> dict[str, dict[str, Any]]:
    ops = run.attributes.get("operations")
    return dict(ops) if isinstance(ops, dict) else {}


def _delta_pct(base: float, cand: float) -> float | None:
    if base == 0:
        return None
    return (cand - base) / base * 100.0


def compare_runs(
    baseline: PerformanceRun,
    candidate: PerformanceRun,
    *,
    threshold_pct: float = 10.0,
    min_samples: int = 3,
    metrics: tuple[str, ...] = ("mean_ms", "p95_ms"),
) -> ComparisonReport:
    base_ops, cand_ops = _ops(baseline), _ops(candidate)
    shared = sorted(set(base_ops) & set(cand_ops))
    regressions: list[Regression] = []
    insufficient: list[str] = []
    compared = 0
    for op in shared:
        b, c = base_ops[op], cand_ops[op]
        b_count = int(b.get("count") or 0)
        c_count = int(c.get("count") or 0)
        if b_count < min_samples or c_count < min_samples:
            insufficient.append(op)
            continue
        compared += 1
        for metric in metrics:
            b_v, c_v = b.get(metric), c.get(metric)
            if not isinstance(b_v, (int, float)) or not isinstance(c_v, (int, float)):
                continue
            delta = _delta_pct(float(b_v), float(c_v))
            if delta is not None and delta > threshold_pct:
                regressions.append(
                    Regression(
                        operation=op,
                        metric=metric,
                        baseline_ms=float(b_v),
                        candidate_ms=float(c_v),
                        delta_pct=delta,
                    )
                )
    return ComparisonReport(
        baseline_ref=baseline.id,
        candidate_ref=candidate.id,
        threshold_pct=threshold_pct,
        min_samples=min_samples,
        regressions=tuple(regressions),
        added=tuple(sorted(set(cand_ops) - set(base_ops))),
        removed=tuple(sorted(set(base_ops) - set(cand_ops))),
        insufficient_data=tuple(insufficient),
        compared=compared,
    )


def detect_regression(
    baseline: PerformanceRun,
    candidate: PerformanceRun,
    *,
    threshold_pct: float = 10.0,
    min_samples: int = 3,
) -> tuple[Regression, ...]:
    return compare_runs(
        baseline,
        candidate,
        threshold_pct=threshold_pct,
        min_samples=min_samples,
    ).regressions
