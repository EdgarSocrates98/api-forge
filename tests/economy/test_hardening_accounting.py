from pathlib import Path

from apiforge.contracts.economy import CostVector, RunLedgerEntry
from apiforge.economy import run_ledger


def _row(run: str, tokens: int | None) -> RunLedgerEntry:
    return RunLedgerEntry(
        run_id=run,
        verb="runtime role:specialist",
        source="envelope",
        cost=CostVector(context_bytes=10, observed_tokens=tokens),
    )


def test_partial_token_measurement_is_never_reported_as_observed(tmp_path: Path) -> None:
    for tokens in (1000, None, None):
        assert run_ledger.append(tmp_path, _row("run-1", tokens))
    stats = run_ledger.stats(tmp_path)
    assert stats["token_coverage"] == {"status": "partial", "observed_rows": 1, "eligible_rows": 3}
    assert stats["observed_tokens"] == "partial"
    assert stats["observed_tokens_measured"] == 1000
    assert stats["tokens_unresolved"] is True


def test_complete_and_unresolved_coverage(tmp_path: Path) -> None:
    run_ledger.append(tmp_path / "a", _row("r", 5))
    run_ledger.append(tmp_path / "a", _row("r", 7))
    complete = run_ledger.stats(tmp_path / "a")
    assert complete["token_coverage"]["status"] == "complete"
    assert complete["observed_tokens"] == 12 and complete["tokens_unresolved"] is False
    run_ledger.append(tmp_path / "b", _row("r", None))
    assert run_ledger.stats(tmp_path / "b")["observed_tokens"] == "unresolved"


def test_auditable_persist_failure_is_surfaced(tmp_path: Path) -> None:
    (tmp_path / ".apiforge" / "economy.jsonl").mkdir(parents=True)
    assert run_ledger.append(tmp_path, _row("r", None)) is False
    assert run_ledger.persist_failures(tmp_path) == 0
    assert run_ledger.append(tmp_path, _row("r", None), auditable=True) is False
    assert run_ledger.persist_failures(tmp_path) == 1
    stats_root = tmp_path
    assert run_ledger.PERSIST_FAILURE in run_ledger.stats(stats_root)["unresolved"]
