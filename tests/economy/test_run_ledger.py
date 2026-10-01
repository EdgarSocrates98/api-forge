import json
from pathlib import Path

import pytest

from apiforge.contracts.economy import CostVector, LedgerRef, RunLedgerEntry
from apiforge.economy import run_ledger
from apiforge.economy.ledger import ledger_path, record, report


def _entry(run_id: str = "run-1", source: str = "contract", size: int = 100) -> RunLedgerEntry:
    return RunLedgerEntry(
        run_id=run_id,
        verb="context capsule",
        source=source,  # type: ignore[arg-type]
        cost=CostVector(context_bytes=size),
        refs=(
            LedgerRef(
                uri="ctx://sha256/" + "b" * 64,
                label="schema:Order",
                provenance="schema-ref:Order",
                size_bytes=size,
            ),
        ),
    )


def test_attribution_rows_leave_legacy_report_unchanged(tmp_path: Path) -> None:
    record(tmp_path, verb="apiforge rules list", detail_level="normal", payload_bytes=500)
    before = report(tmp_path)
    run_ledger.append(tmp_path, _entry())
    after = report(tmp_path)
    assert after["payload_bytes"] == before["payload_bytes"] == 500
    assert after["tokens_unresolved"] is True


def test_stats_reads_legacy_rows_into_their_own_bucket(tmp_path: Path) -> None:
    record(tmp_path, verb="apiforge rules list", detail_level="normal", payload_bytes=500)
    run_ledger.append(tmp_path, _entry(source="contract", size=120))
    run_ledger.append(tmp_path, _entry(source="code", size=80))
    stats = run_ledger.stats(tmp_path)
    assert stats["legacy"] == {"calls": 1, "payload_bytes": 500}
    assert stats["attributed_bytes"] == 200
    assert set(stats["by_source"]) == {"code", "contract"}
    assert sum(item["context_bytes"] for item in stats["by_source"].values()) == 200


def test_tokens_stay_unresolved_without_observed_usage(tmp_path: Path) -> None:
    run_ledger.append(tmp_path, _entry())
    stats = run_ledger.stats(tmp_path)
    assert stats["tokens_unresolved"] is True
    assert stats["observed_tokens"] == "unresolved"


def test_malformed_lines_are_skipped_and_counted(tmp_path: Path) -> None:
    path = ledger_path(tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text(
        "not json\n" + json.dumps({"schema": "apiforge/run-ledger-entry/v1"}) + "\n",
        encoding="utf-8",
    )
    stats = run_ledger.stats(tmp_path)
    assert stats["diagnostics"]["malformed_lines"] == 2
    assert stats["entries"] == 0


def test_explain_names_the_rule_behind_each_ref(tmp_path: Path) -> None:
    run_ledger.append(tmp_path, _entry())
    explained = run_ledger.explain(tmp_path, "run-1")
    assert explained["method"].endswith("no model call")
    assert explained["refs"][0]["rule"] == "schema-ref:Order"
    assert "referenced by the target contract" in explained["refs"][0]["reason"]
    assert explained["by_source"]["contract"]["share"] == 1.0


def test_explain_unknown_run_is_refused(tmp_path: Path) -> None:
    with pytest.raises(run_ledger.EconomyError) as error:
        run_ledger.explain(tmp_path, "missing")
    assert error.value.code == "AF-ECONOMY-RUN-NOT-FOUND"
    assert error.value.field == "run_id"
