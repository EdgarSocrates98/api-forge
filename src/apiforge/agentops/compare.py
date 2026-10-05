"""§55 run comparison: deterministic a/b over the declared axis set.

The winner per axis is decided by the axis direction (lower-is-better for
tokens/cost/latency, higher for quality/evidence coverage); an axis whose
either side is unresolved stays unresolved — never a tie by absence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from apiforge.agentops.inspect import inspect_run
from apiforge.contracts.agentops_report import ComparisonAxis, RunComparison, RunInspection
from apiforge.core.models import JsonValue

_LOWER_IS_BETTER = {"tokens", "cost", "latency", "context"}


def _axis(
    axis: str,
    a_value: JsonValue | None,
    b_value: JsonValue | None,
    *,
    lower_better: bool,
    detail: str = "",
) -> ComparisonAxis:
    if not isinstance(a_value, (int, float)) or not isinstance(b_value, (int, float)):
        return ComparisonAxis(
            axis=axis,
            a=a_value,
            b=b_value,
            verdict="unresolved",
            detail=detail or "one side has no numeric value",
        )
    delta = float(b_value) - float(a_value)
    verdict: Literal["a", "b", "tie", "unresolved"]
    if delta == 0:
        verdict = "tie"
    elif lower_better:
        verdict = "a" if delta > 0 else "b"
    else:
        verdict = "a" if delta < 0 else "b"
    return ComparisonAxis(
        axis=axis, a=a_value, b=b_value, delta=delta, verdict=verdict, detail=detail
    )


def compare_runs(root: Path, run_a: str, run_b: str) -> RunComparison:
    """Compare two runs over the §55 axis set."""
    root = Path(root)
    inspection_a = inspect_run(root, run_a)
    inspection_b = inspect_run(root, run_b)
    unresolved: list[str] = []

    def metric(inspection: RunInspection, section: str, name: str) -> JsonValue | None:
        for value in inspection.sections:
            if value.name == section:
                for item in value.metrics:
                    if item.name == name:
                        return item.value
        return None

    def quality(inspection: RunInspection) -> float | None:
        for name in ("context_precision", "context_recall", "context_density"):
            value = metric(inspection, "context", name)
            if isinstance(value, (int, float)):
                return float(value)
        return None

    axes = (
        _axis(
            "quality",
            quality(inspection_a),
            quality(inspection_b),
            lower_better=False,
            detail="first available of precision/recall/density",
        ),
        _axis(
            "tokens",
            metric(inspection_a, "context", "tokens"),
            metric(inspection_b, "context", "tokens"),
            lower_better=True,
        ),
        _axis(
            "cost",
            metric(inspection_a, "models", "cost"),
            metric(inspection_b, "models", "cost"),
            lower_better=True,
            detail="cost requires declared pricing on both sides",
        ),
        _axis(
            "latency",
            metric(inspection_a, "models", "latency_ms"),
            metric(inspection_b, "models", "latency_ms"),
            lower_better=True,
        ),
        _axis(
            "context",
            metric(inspection_a, "context", "bytes"),
            metric(inspection_b, "context", "bytes"),
            lower_better=True,
        ),
        _axis(
            "evidence",
            metric(inspection_a, "evidence", "refs"),
            metric(inspection_b, "evidence", "refs"),
            lower_better=False,
        ),
        _axis(
            "tools",
            metric(inspection_a, "tools", "failures"),
            metric(inspection_b, "tools", "failures"),
            lower_better=True,
            detail="compares failure counts",
        ),
        _axis(
            "agents",
            metric(inspection_a, "agents", "agents"),
            metric(inspection_b, "agents", "agents"),
            lower_better=True,
            detail="compares distinct agent counts",
        ),
    )
    for axis in axes:
        if axis.verdict == "unresolved":
            unresolved.append(f"axis {axis.axis}: {axis.detail}")
    unresolved.extend(
        f"run {side}: {item}"
        for side, inspection in (("a", inspection_a), ("b", inspection_b))
        for item in inspection.unresolved
    )
    return RunComparison(run_a=run_a, run_b=run_b, axes=axes, unresolved=tuple(unresolved))


__all__ = ["compare_runs"]
