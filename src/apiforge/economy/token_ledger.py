"""§19 Token Ledger: usage rows roll up per basis — never mixed.

Provider Usage -> Token Ledger -> Agent Budget -> Task Budget -> Run
Budget. ``build_ledger`` produces per-basis ``TokenTotals`` at run,
task and agent granularity; ``observed`` and ``estimated`` never share a
sum and ``unresolved`` rows are counted, not added.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.token_economics import (
    TokenAccounting,
    TokenLedger,
    TokenLedgerEntry,
    TokenTotals,
    UsageBasis,
)

LEDGER_DIR = Path("economy/token_usage")


def entry_id(run_id: str, accounting: TokenAccounting, recorded_at: str) -> str:
    """Deterministic ``usage:<sha16>`` — replay produces the same id."""
    payload = json.dumps(
        {
            "run_id": run_id,
            "accounting": accounting.model_dump(mode="json"),
            "recorded_at": recorded_at,
        },
        sort_keys=True,
    )
    return f"usage:{hashlib.sha256(payload.encode()).hexdigest()[:16]}"


def transcript_accounting(model: str, usage: dict[str, int], *, recorded: str) -> TokenAccounting:
    """Adapt a ``read_transcript`` per-model row to an observed accounting."""
    return TokenAccounting(
        basis="observed",
        input_tokens=usage.get("input_tokens") or None,
        output_tokens=usage.get("output_tokens") or None,
        cached_input_tokens=usage.get("cache_read_input_tokens") or None,
        cache_creation_tokens=usage.get("cache_creation_input_tokens") or None,
        reasoning_tokens=usage.get("reasoning_tokens") or None,
        model=model,
        source=f"transcript:{recorded}",
    )


def estimated_accounting(tokens: int, *, method: str, model: str | None = None) -> TokenAccounting:
    """Build a labeled estimated accounting; ``method`` is mandatory."""
    return TokenAccounting(
        basis="estimated",
        input_tokens=tokens,
        model=model,
        source="estimate",
        estimation_method=method,
    )


def _add(totals: TokenTotals, accounting: TokenAccounting) -> TokenTotals:
    return TokenTotals(
        input_tokens=totals.input_tokens + (accounting.input_tokens or 0),
        output_tokens=totals.output_tokens + (accounting.output_tokens or 0),
        cached_input_tokens=totals.cached_input_tokens + (accounting.cached_input_tokens or 0),
        cache_creation_tokens=totals.cache_creation_tokens
        + (accounting.cache_creation_tokens or 0),
        reasoning_tokens=totals.reasoning_tokens + (accounting.reasoning_tokens or 0),
        entries=totals.entries + 1,
    )


def build_ledger(run_id: str, entries: list[TokenLedgerEntry]) -> TokenLedger:
    """Aggregate entries into per-basis totals; bases never merge."""
    observed, estimated, unresolved = TokenTotals(), TokenTotals(), 0
    by_task: dict[str, dict[UsageBasis, TokenTotals]] = {}
    by_agent: dict[str, dict[UsageBasis, TokenTotals]] = {}
    for entry in entries:
        accounting = entry.accounting
        basis = accounting.basis
        if basis == "unresolved":
            unresolved += 1
            continue
        if basis == "observed":
            observed = _add(observed, accounting)
        else:
            estimated = _add(estimated, accounting)
        for scope, bucket in ((entry.task_id, by_task), (entry.agent, by_agent)):
            if scope is None:
                continue
            axes = bucket.setdefault(scope, {})
            axes[basis] = _add(axes.get(basis, TokenTotals()), accounting)
    return TokenLedger(
        run_id=run_id,
        observed=observed,
        estimated=estimated,
        unresolved_entries=unresolved,
        by_task={k: dict(v) for k, v in sorted(by_task.items())},
        by_agent={k: dict(v) for k, v in sorted(by_agent.items())},
    )


def append_usage(root: Path, entry: TokenLedgerEntry) -> Path:
    """Append a usage row; the file is append-only like every economy ledger."""
    path = root / LEDGER_DIR / f"{entry.run_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.model_dump(mode="json")) + "\n")
    return path


def load_entries(root: Path, run_id: str) -> tuple[list[TokenLedgerEntry], int]:
    """Read a run's usage rows; unparseable lines are counted, not fatal."""
    path = root / LEDGER_DIR / f"{run_id}.jsonl"
    entries: list[TokenLedgerEntry] = []
    unparsed = 0
    if not path.is_file():
        return entries, 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entries.append(TokenLedgerEntry.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValueError):
            unparsed += 1
    return entries, unparsed


def load_usage_estimate(path: Path) -> dict[str, Any]:
    """Read a declared estimate yaml for §22 reconciliation input."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


__all__ = [
    "LEDGER_DIR",
    "append_usage",
    "build_ledger",
    "entry_id",
    "estimated_accounting",
    "load_entries",
    "load_usage_estimate",
    "transcript_accounting",
]
