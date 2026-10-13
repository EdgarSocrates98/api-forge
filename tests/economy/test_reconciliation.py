"""§22 Budget Reconciliation: estimated vs observed with calibration error."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.economy import CostVector, RunLedgerEntry
from apiforge.contracts.token_economics import ReconciliationAxis
from apiforge.economy.reconciliation import estimate_axis, reconcile, run_observed
from apiforge.economy.run_ledger import append


def _row(
    run_id: str,
    *,
    tokens: int | None = None,
    tool_bytes: int = 0,
    duration_ms: int = 0,
    verb: str = "context capsule",
) -> RunLedgerEntry:
    return RunLedgerEntry(
        run_id=run_id,
        verb=verb,
        source="graph",
        cost=CostVector(
            tool_result_bytes=tool_bytes,
            duration_ms=duration_ms,
            observed_tokens=tokens,
        ),
    )


def test_reconcile_all_axes() -> None:
    result = reconcile(
        "run:r1",
        ReconciliationAxis(tokens=100, cost=1.0, tool_calls=4, elapsed_ms=2000),
        ReconciliationAxis(tokens=110, cost=0.9, tool_calls=5, elapsed_ms=1800),
    )
    assert result.calibration_error["tokens"] == 0.1
    assert result.calibration_error["cost"] == -0.1
    assert result.calibration_error["tool_calls"] == 0.25
    assert result.calibration_error["elapsed_ms"] == -0.1
    assert result.unresolved == ()


def test_reconcile_missing_side_is_unresolved() -> None:
    result = reconcile(
        "run:r1",
        ReconciliationAxis(tokens=100),
        ReconciliationAxis(tokens=110),
    )
    assert "cost" in result.unresolved
    assert "tokens" not in result.unresolved


def test_reconcile_zero_estimate_with_observed_unresolved() -> None:
    result = reconcile(
        "run:r1",
        ReconciliationAxis(tokens=0, tool_calls=0),
        ReconciliationAxis(tokens=50, tool_calls=0),
    )
    assert "tokens" in result.unresolved
    assert result.calibration_error["tool_calls"] == 0.0


def test_estimate_axis_maps_aliases() -> None:
    axis = estimate_axis({"tokens": 10, "cost_usd": 0.5, "tool_calls": 2, "duration_ms": 100})
    assert axis.cost == 0.5
    assert axis.elapsed_ms == 100


def test_run_observed_sums_rows(tmp_path: Path) -> None:
    append(tmp_path, _row("r1", tokens=10, tool_bytes=5, duration_ms=100))
    append(tmp_path, _row("r1", tokens=15, duration_ms=50))
    append(tmp_path, _row("other", tokens=99))
    axis = run_observed(tmp_path, "r1", observed_cost=0.25)
    assert axis.tokens == 25
    assert axis.tool_calls == 1
    assert axis.elapsed_ms == 150
    assert axis.cost == 0.25


def test_run_observed_no_tokens_is_none(tmp_path: Path) -> None:
    append(tmp_path, _row("r1"))
    axis = run_observed(tmp_path, "r1")
    assert axis.tokens is None
    assert axis.cost is None


def test_run_observed_empty_run(tmp_path: Path) -> None:
    axis = run_observed(tmp_path, "ghost")
    assert axis.tokens is None
    assert axis.tool_calls is None
    assert axis.elapsed_ms is None


def test_end_to_end_reconcile(tmp_path: Path) -> None:
    append(tmp_path, _row("r2", tokens=120, tool_bytes=1, duration_ms=300))
    result = reconcile(
        "run:r2",
        estimate_axis({"tokens": 100, "tool_calls": 2, "elapsed_ms": 250}),
        run_observed(tmp_path, "r2"),
    )
    assert result.calibration_error["tokens"] == 0.2
    assert result.calibration_error["tool_calls"] == -0.5
    assert "cost" in result.unresolved
