"""§34 Model Scorecard — deterministic fold of ModelEvaluation records into
per provider/model history segmented by task class. Metrics with no
observations stay ``None`` and are named in ``unresolved`` — never zeroed.
"""

from __future__ import annotations

from collections.abc import Sequence

from apiforge.contracts.model_routing import (
    ModelEvaluation,
    ModelScorecard,
    ModelTaskClass,
)

_METRICS = (
    "quality",
    "tool_selection_accuracy",
    "evidence_correctness",
    "structured_output_reliability",
)


def aggregate_scorecards(
    evaluations: Sequence[ModelEvaluation],
) -> dict[tuple[str, str, ModelTaskClass], ModelScorecard]:
    """Fold evaluations into scorecards keyed by (provider, model, class)."""
    buckets: dict[tuple[str, str, ModelTaskClass], list[ModelEvaluation]] = {}
    for row in evaluations:
        buckets.setdefault((row.provider, row.model, row.task_class), []).append(row)
    return {key: _fold(key, rows) for key, rows in buckets.items()}


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def _fold(key: tuple[str, str, ModelTaskClass], rows: list[ModelEvaluation]) -> ModelScorecard:
    provider, model, task_class = key
    unresolved: list[str] = []
    metrics: dict[str, float | None] = {}
    for metric in _METRICS:
        observed = [float(getattr(row, metric)) for row in rows if getattr(row, metric) is not None]
        metrics[metric] = sum(observed) / len(observed) if observed else None
        if not observed:
            unresolved.append(metric)
    latencies = [float(row.latency_ms) for row in rows if row.latency_ms is not None]
    costs = [float(row.cost) for row in rows if row.cost is not None]
    if not latencies:
        unresolved.append("latency_p50_ms")
    if not costs:
        unresolved.append("cost_mean")
    failures = [row.failed for row in rows]
    latest = max(row.recorded_at for row in rows)
    return ModelScorecard(
        provider=provider,
        model=model,
        task_class=task_class,
        evaluation_count=len(rows),
        quality=metrics["quality"],
        tool_selection_accuracy=metrics["tool_selection_accuracy"],
        evidence_correctness=metrics["evidence_correctness"],
        structured_output_reliability=metrics["structured_output_reliability"],
        latency_p50_ms=_median(latencies) if latencies else None,
        cost_mean=sum(costs) / len(costs) if costs else None,
        failure_rate=sum(1 for flag in failures if flag) / len(failures),
        freshness_state="fresh",
        observed_at=latest,
        unresolved=tuple(sorted(unresolved)),
    )


def scorecard_map(
    scorecards: dict[tuple[str, str, ModelTaskClass], ModelScorecard],
    task_class: ModelTaskClass | None = None,
) -> dict[tuple[str, str], ModelScorecard]:
    """Flatten to (provider, model); a task_class filter keeps segmentation."""
    return {
        (key[0], key[1]): card
        for key, card in scorecards.items()
        if task_class is None or key[2] == task_class
    }


__all__ = ["aggregate_scorecards", "scorecard_map"]
