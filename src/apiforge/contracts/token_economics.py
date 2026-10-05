"""Unified Token Economics contracts (step11 phase 3, prompt §19–§22).

Pipeline: Provider Usage -> Token Ledger -> Agent/Task/Run budgets ->
Provider Cost -> Economy Report. The three bases — ``observed``,
``estimated``, ``unresolved`` — are never mixed inside one sum.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract

UsageBasis = Literal["observed", "estimated", "unresolved"]

_TOKEN_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "cache_creation_tokens",
    "reasoning_tokens",
)


class TokenAccounting(VersionedContract):
    """§20 usage accounting for one unit of provider work (§20).

    ``basis`` labels the whole row: ``observed`` rows come from a provider
    transcript/report, ``estimated`` rows carry a declared estimation method,
    ``unresolved`` rows record that usage is unknown — fields stay ``None``.
    """

    schema: Literal["apiforge/token-accounting/v1"] = "apiforge/token-accounting/v1"  # type: ignore[assignment]
    basis: UsageBasis
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    cached_input_tokens: int | None = Field(default=None, ge=0)
    cache_creation_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    model: str | None = None
    source: str = ""
    estimation_method: str | None = None

    @model_validator(mode="after")
    def basis_consistency(self) -> TokenAccounting:
        fields = [getattr(self, name) for name in _TOKEN_FIELDS]
        if self.basis == "unresolved":
            if any(value is not None for value in fields):
                raise ValueError("unresolved accounting cannot carry token counts")
        elif all(value is None for value in fields):
            raise ValueError("observed/estimated accounting requires at least one count")
        if self.basis == "estimated" and not self.estimation_method:
            raise ValueError("estimated accounting requires a declared estimation_method")
        return self

    def total(self) -> int:
        """Sum of present fields; ``None`` fields contribute zero."""
        return sum(value or 0 for value in (getattr(self, name) for name in _TOKEN_FIELDS))


class TokenLedgerEntry(VersionedContract):
    """One usage row in the §19 pipeline: who consumed what, on what basis."""

    schema: Literal["apiforge/token-ledger-entry/v1"] = "apiforge/token-ledger-entry/v1"  # type: ignore[assignment]
    entry_id: str = Field(pattern=r"^usage:[0-9a-f]{16}$")
    run_id: str = Field(min_length=1)
    task_id: str | None = None
    agent: str | None = None
    # Correlates one token row with its provider/model span.
    model_call_id: str | None = None
    accounting: TokenAccounting
    recorded_at: str
    provenance: tuple[str, ...] = ()


class TokenTotals(VersionedContract):
    """Summed usage for one basis bucket; bases never merge."""

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    cache_creation_tokens: int = Field(default=0, ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    entries: int = Field(default=0, ge=0)

    def total(self) -> int:
        return (
            self.input_tokens
            + self.output_tokens
            + self.cached_input_tokens
            + self.cache_creation_tokens
            + self.reasoning_tokens
        )


class TokenLedger(VersionedContract):
    """§19 run rollup: per-basis totals at agent, task and run granularity."""

    schema: Literal["apiforge/token-ledger/v1"] = "apiforge/token-ledger/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    observed: TokenTotals = Field(default_factory=TokenTotals)
    estimated: TokenTotals = Field(default_factory=TokenTotals)
    unresolved_entries: int = Field(default=0, ge=0)
    by_task: dict[str, dict[UsageBasis, TokenTotals]] = Field(default_factory=dict)
    by_agent: dict[str, dict[UsageBasis, TokenTotals]] = Field(default_factory=dict)
    cost_basis_missing: tuple[str, ...] = ()


class ProviderPricing(VersionedContract):
    """§21 versioned price row — declared, never inferred (§21)."""

    schema: Literal["apiforge/provider-pricing/v1"] = "apiforge/provider-pricing/v1"  # type: ignore[assignment]
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    effective_at: str = Field(min_length=1)
    currency: str = Field(min_length=1)
    source: str = Field(min_length=1)
    input_per_mtok: float | None = Field(default=None, ge=0)
    output_per_mtok: float | None = Field(default=None, ge=0)
    cached_input_per_mtok: float | None = Field(default=None, ge=0)
    cache_creation_per_mtok: float | None = Field(default=None, ge=0)
    reasoning_per_mtok: float | None = Field(default=None, ge=0)
    notes: str = ""


class ProviderCost(VersionedContract):
    """Cost for one TokenAccounting under one ProviderPricing (§19 last hop)."""

    schema: Literal["apiforge/provider-cost/v1"] = "apiforge/provider-cost/v1"  # type: ignore[assignment]
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    currency: str = Field(min_length=1)
    components: dict[str, float] = Field(default_factory=dict)
    total: float | None = None
    basis: UsageBasis = "observed"
    missing_rates: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class ReconciliationAxis(VersionedContract):
    """One side (estimated or observed) of a §22 reconciliation."""

    tokens: int | None = Field(default=None, ge=0)
    cost: float | None = Field(default=None, ge=0)
    tool_calls: int | None = Field(default=None, ge=0)
    elapsed_ms: int | None = Field(default=None, ge=0)


class BudgetReconciliation(VersionedContract):
    """§22 estimated-vs-observed comparison with per-axis calibration error.

    ``calibration_error[axis] = (observed - estimated) / estimated``; an axis
    missing on either side lands in ``unresolved``, never silently zero.
    """

    schema: Literal["apiforge/budget-reconciliation/v1"] = "apiforge/budget-reconciliation/v1"  # type: ignore[assignment]
    scope: str = Field(min_length=1)
    estimated: ReconciliationAxis = Field(default_factory=ReconciliationAxis)
    observed: ReconciliationAxis = Field(default_factory=ReconciliationAxis)
    calibration_error: dict[str, float] = Field(default_factory=dict)
    unresolved: tuple[str, ...] = ()


__all__ = [
    "BudgetReconciliation",
    "ProviderCost",
    "ProviderPricing",
    "ReconciliationAxis",
    "TokenAccounting",
    "TokenLedger",
    "TokenLedgerEntry",
    "TokenTotals",
    "UsageBasis",
]
