"""§22 Budget Reconciliation: estimated vs observed, per axis, after a run.

Axes: tokens, cost, tool_calls, elapsed_ms. ``calibration_error[axis]`` is
``(observed - estimated) / estimated``; an axis missing on either side —
or an estimate of zero against a positive observed — lands in
``unresolved`` rather than being silently treated as perfect or zero.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.contracts.token_economics import (
    BudgetReconciliation,
    ReconciliationAxis,
)
from apiforge.economy import run_ledger

_AXES = ("tokens", "cost", "tool_calls", "elapsed_ms")


def estimate_axis(raw: dict[str, Any]) -> ReconciliationAxis:
    """Build the estimated side from a declared estimate mapping."""
    return ReconciliationAxis(
        tokens=raw.get("tokens"),
        cost=raw.get("cost") or raw.get("cost_usd"),
        tool_calls=raw.get("tool_calls"),
        elapsed_ms=raw.get("elapsed_ms") or raw.get("duration_ms"),
    )


def run_observed(
    root: Path, run_id: str, *, observed_cost: float | None = None
) -> ReconciliationAxis:
    """Derive the observed side from the run's attribution rows.

    ``tokens`` is the measured sum (``tokens_partial_coverage`` in
    ``unresolved`` flags partial coverage at reconcile time); ``cost`` is
    only present when the caller supplies a priced value — the ledger never
    invents one; ``tool_calls`` counts rows carrying tool bytes;
    ``elapsed_ms`` sums row durations.
    """
    rows = [row for row in run_ledger.entries(root)[0] if row.run_id == run_id]
    measured = sum(row.cost.observed_tokens or 0 for row in rows)
    has_tokens = any(row.cost.observed_tokens is not None for row in rows)
    return ReconciliationAxis(
        tokens=measured if has_tokens else None,
        cost=observed_cost,
        tool_calls=sum(1 for row in rows if row.cost.tool_result_bytes > 0) or None,
        elapsed_ms=sum(row.cost.duration_ms for row in rows) or None,
    )


def reconcile(
    scope: str,
    estimated: ReconciliationAxis,
    observed: ReconciliationAxis,
) -> BudgetReconciliation:
    """Compare both sides per axis; unresolved axes stay named."""
    calibration: dict[str, float] = {}
    unresolved: list[str] = []
    for axis in _AXES:
        est = getattr(estimated, axis)
        obs = getattr(observed, axis)
        if est is None or obs is None:
            unresolved.append(axis)
        elif est == 0:
            if obs == 0:
                calibration[axis] = 0.0
            else:
                unresolved.append(axis)
        else:
            calibration[axis] = round((obs - est) / est, 4)
    return BudgetReconciliation(
        scope=scope,
        estimated=estimated,
        observed=observed,
        calibration_error=calibration,
        unresolved=tuple(sorted(unresolved)),
    )


__all__ = ["estimate_axis", "reconcile", "run_observed"]
