"""§20–§22 contract invariants: basis discipline, pricing, reconciliation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from apiforge.contracts.token_economics import (
    BudgetReconciliation,
    ProviderCost,
    ProviderPricing,
    ReconciliationAxis,
    TokenAccounting,
    TokenLedger,
    TokenLedgerEntry,
    TokenTotals,
)


def test_observed_accounting_total() -> None:
    accounting = TokenAccounting(
        basis="observed",
        input_tokens=100,
        output_tokens=50,
        cached_input_tokens=20,
        model="m1",
    )
    assert accounting.total() == 170


def test_unresolved_accounting_carries_no_counts() -> None:
    accounting = TokenAccounting(basis="unresolved", source="provider-silent")
    assert accounting.total() == 0


def test_unresolved_rejects_counts() -> None:
    with pytest.raises(ValidationError):
        TokenAccounting(basis="unresolved", input_tokens=10)


def test_estimated_requires_method() -> None:
    with pytest.raises(ValidationError):
        TokenAccounting(basis="estimated", input_tokens=10)


def test_estimated_labeled() -> None:
    accounting = TokenAccounting(basis="estimated", input_tokens=10, estimation_method="bytes/4")
    assert accounting.basis == "estimated"


def test_ledger_entry_id_shape() -> None:
    entry = TokenLedgerEntry(
        entry_id="usage:0123456789abcdef",
        run_id="r1",
        accounting=TokenAccounting(basis="observed", input_tokens=5),
        recorded_at="2026-01-01T00:00:00Z",
    )
    assert entry.accounting.basis == "observed"


def test_ledger_keeps_bases_separate() -> None:
    ledger = TokenLedger(
        run_id="r1",
        observed=TokenTotals(input_tokens=100, entries=1),
        estimated=TokenTotals(input_tokens=50, entries=1),
        unresolved_entries=1,
    )
    assert ledger.observed.input_tokens == 100
    assert ledger.estimated.input_tokens == 50


def test_provider_pricing_fields() -> None:
    row = ProviderPricing(
        provider="p",
        model="m",
        effective_at="2026-01-01",
        currency="USD",
        source="declared:test",
        input_per_mtok=1.0,
        output_per_mtok=2.0,
    )
    assert row.reasoning_per_mtok is None


def test_provider_cost_names_gaps() -> None:
    cost = ProviderCost(
        provider="p",
        model="m",
        currency="USD",
        components={"input": 1.0},
        total=1.0,
        missing_rates=("reasoning_per_mtok",),
        unresolved=("reasoning_tokens",),
    )
    assert cost.total == 1.0


def test_reconciliation_axis_optional() -> None:
    axis = ReconciliationAxis(tokens=10)
    assert axis.cost is None


def test_budget_reconciliation_carries_unresolved() -> None:
    recon = BudgetReconciliation(
        scope="run:r1",
        estimated=ReconciliationAxis(tokens=100),
        observed=ReconciliationAxis(tokens=110),
        calibration_error={"tokens": 0.1},
        unresolved=("cost",),
    )
    assert recon.calibration_error["tokens"] == 0.1
