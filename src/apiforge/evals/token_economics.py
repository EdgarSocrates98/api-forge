"""Deterministic token-economics evals: usage rows + pricing + estimate ->
ledger totals, cost components and §22 calibration error vs expectations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.token_economics import (
    ProviderPricing,
    ReconciliationAxis,
    TokenAccounting,
    TokenLedgerEntry,
)
from apiforge.economy.pricing import cost_for, price_for
from apiforge.economy.reconciliation import reconcile
from apiforge.economy.token_ledger import build_ledger, entry_id


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"token-economics corpus {corpus} empty or duplicated"
        )
    return cases


def _entries(case: dict[str, Any]) -> list[TokenLedgerEntry]:
    rows: list[TokenLedgerEntry] = []
    for index, spec in enumerate(case.get("usage_rows") or ()):
        accounting = TokenAccounting.model_validate(
            {key: value for key, value in spec.items() if key not in ("task_id", "agent")}
        )
        recorded = str(case.get("recorded_at", f"{case['id']}:{index}"))
        rows.append(
            TokenLedgerEntry(
                entry_id=entry_id(case["id"], accounting, recorded),
                run_id=case.get("run_id", case["id"]),
                task_id=spec.get("task_id"),
                agent=spec.get("agent"),
                accounting=accounting,
                recorded_at=recorded,
            )
        )
    return rows


def _observed_cost(case: dict[str, Any]) -> float | None:
    """Price the run's observed accounting against the case pricing rows."""
    rows = case.get("pricing_rows") or ()
    usage_spec = case.get("cost_accounting")
    if not rows or usage_spec is None:
        return None
    pricing_rows = tuple(ProviderPricing.model_validate(row) for row in rows)
    accounting = TokenAccounting.model_validate(usage_spec)
    model = accounting.model or str(pricing_rows[0].model)
    row = price_for(pricing_rows, str(pricing_rows[0].provider), model)
    if row is None:
        return None
    return cost_for(accounting, row).total


def _close(actual: float, expected: float, tol: float = 1e-4) -> bool:
    return abs(actual - expected) <= tol


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    ledger = build_ledger(case.get("run_id", case["id"]), _entries(case))
    observed_cost = _observed_cost(case)
    overrides = case.get("observed") or {}
    observed = ReconciliationAxis(
        tokens=ledger.observed.total() if ledger.observed.entries else None,
        cost=observed_cost,
        tool_calls=overrides.get("tool_calls"),
        elapsed_ms=overrides.get("elapsed_ms"),
    )
    result = reconcile(
        f"run:{case['id']}",
        ReconciliationAxis.model_validate(case.get("estimate") or {}),
        observed,
    )
    failures: list[str] = []
    expect = case.get("expect") or {}
    checks = (
        ("observed_input", ledger.observed.input_tokens),
        ("observed_output", ledger.observed.output_tokens),
        ("estimated_input", ledger.estimated.input_tokens),
        ("unresolved_entries", ledger.unresolved_entries),
        ("observed_total", ledger.observed.total()),
    )
    for name, actual in checks:
        if name in expect and actual != expect[name]:
            failures.append(f"{name} {actual} != {expect[name]}")
    if "cost_total" in expect and (
        observed_cost is None or not _close(observed_cost, float(expect["cost_total"]), 1e-6)
    ):
        failures.append(f"cost_total {observed_cost} != {expect['cost_total']}")
    for axis, spec in (expect.get("calibration") or {}).items():
        calib = result.calibration_error.get(axis)
        if calib is None or not _close(calib, float(spec)):
            failures.append(f"calibration[{axis}] {calib} != {spec}")
    for axis in expect.get("unresolved_axes") or ():
        if axis not in result.unresolved:
            failures.append(f"axis {axis} expected unresolved")
    for axis in expect.get("resolved_axes") or ():
        if axis in result.unresolved:
            failures.append(f"axis {axis} expected resolved")
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_token_economics(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results = [_run_case(case) for case in cases]
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/token-economics-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_token_economics"]
