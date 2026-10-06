"""§19 Token Ledger: rows roll up per basis — never mixed."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.token_economics import TokenAccounting, TokenLedgerEntry
from apiforge.economy.token_ledger import (
    append_usage,
    build_ledger,
    entry_id,
    estimated_accounting,
    load_entries,
    transcript_accounting,
)


def _entry(
    run_id: str,
    accounting: TokenAccounting,
    *,
    task_id: str | None = None,
    agent: str | None = None,
    recorded_at: str = "2026-01-01T00:00:00Z",
) -> TokenLedgerEntry:
    return TokenLedgerEntry(
        entry_id=entry_id(run_id, accounting, recorded_at),
        run_id=run_id,
        task_id=task_id,
        agent=agent,
        accounting=accounting,
        recorded_at=recorded_at,
    )


def test_entry_id_deterministic() -> None:
    accounting = TokenAccounting(basis="observed", input_tokens=10)
    assert entry_id("r1", accounting, "t") == entry_id("r1", accounting, "t")


def test_transcript_adapter_maps_cache_fields() -> None:
    usage = {
        "input_tokens": 10,
        "output_tokens": 5,
        "cache_read_input_tokens": 3,
        "cache_creation_input_tokens": 2,
        "messages": 1,
    }
    accounting = transcript_accounting("m", usage, recorded="t.jsonl")
    assert accounting.basis == "observed"
    assert accounting.cached_input_tokens == 3
    assert accounting.cache_creation_tokens == 2
    assert accounting.reasoning_tokens is None


def test_build_ledger_never_mixes_bases() -> None:
    rows = [
        _entry(
            "r", TokenAccounting(basis="observed", input_tokens=100, output_tokens=10), task_id="t1"
        ),
        _entry(
            "r",
            TokenAccounting(basis="estimated", input_tokens=90, estimation_method="x"),
            task_id="t1",
            agent="planner",
        ),
        _entry("r", TokenAccounting(basis="unresolved", source="silent")),
    ]
    ledger = build_ledger("r", rows)
    assert ledger.observed.input_tokens == 100
    assert ledger.observed.entries == 1
    assert ledger.estimated.input_tokens == 90
    assert ledger.unresolved_entries == 1
    # task rollup keeps bases apart too
    assert ledger.by_task["t1"]["observed"].input_tokens == 100
    assert ledger.by_task["t1"]["estimated"].input_tokens == 90
    assert ledger.by_agent["planner"]["estimated"].input_tokens == 90


def test_append_and_load_roundtrip(tmp_path: Path) -> None:
    accounting = TokenAccounting(basis="observed", input_tokens=7)
    entry = _entry("run-1", accounting)
    append_usage(tmp_path, entry)
    loaded, unparsed = load_entries(tmp_path, "run-1")
    assert len(loaded) == 1
    assert loaded[0].accounting.input_tokens == 7
    assert unparsed == 0


def test_load_missing_run_is_empty(tmp_path: Path) -> None:
    loaded, unparsed = load_entries(tmp_path, "ghost")
    assert loaded == [] and unparsed == 0


def test_load_skips_malformed_lines(tmp_path: Path) -> None:
    path = tmp_path / "economy" / "token_usage" / "r.jsonl"
    path.parent.mkdir(parents=True)
    path.write_text('{"bad": 1}\nnot-json\n', encoding="utf-8")
    loaded, unparsed = load_entries(tmp_path, "r")
    assert loaded == [] and unparsed == 2


def test_estimated_accounting_labeled() -> None:
    accounting = estimated_accounting(42, method="bytes/4")
    assert accounting.basis == "estimated"
    assert accounting.estimation_method == "bytes/4"
