"""Versioned economy contracts: per-emission cost vectors and run ledger entries."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

LedgerSource = Literal["graph", "contract", "code", "knowledge", "filesystem", "envelope"]


class CostVector(VersionedContract):
    """Measured cost of one emission; tokens are observed or left unresolved."""

    context_bytes: int = Field(default=0, ge=0)
    tool_result_bytes: int = Field(default=0, ge=0)
    expansions: int = Field(default=0, ge=0)
    cache_hits: int = Field(default=0, ge=0)
    duration_ms: int = Field(default=0, ge=0)
    observed_tokens: int | None = Field(default=None, ge=0)


class LedgerRef(VersionedContract):
    """One ref attributed by a ledger entry, with the rule that selected it."""

    uri: str = Field(min_length=1)
    label: str = Field(min_length=1)
    provenance: str = Field(min_length=1)
    size_bytes: int = Field(ge=0)


class RunLedgerEntry(VersionedContract):
    """Attribution row appended to economy.jsonl alongside legacy transport rows."""

    schema: Literal["apiforge/run-ledger-entry/v1"] = "apiforge/run-ledger-entry/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    verb: str = Field(min_length=1)
    detail_level: str = "normal"
    source: LedgerSource
    cost: CostVector = Field(default_factory=CostVector)
    refs: tuple[LedgerRef, ...] = ()
