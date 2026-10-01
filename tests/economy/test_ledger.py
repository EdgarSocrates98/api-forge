"""Economy ledger: measured bytes per call; tokens unresolved without transcript."""

import json
from pathlib import Path

from apiforge.economy.ledger import ledger_path, record, report


def test_record_appends_jsonl(tmp_path: Path) -> None:
    record(tmp_path, verb="rules list", detail_level="normal", payload_bytes=120)
    record(tmp_path, verb="rules list", detail_level="summary", payload_bytes=60)
    lines = ledger_path(tmp_path).read_text().strip().splitlines()
    assert len(lines) == 2
    entry = json.loads(lines[0])
    assert entry == {"verb": "rules list", "detail_level": "normal", "payload_bytes": 120}


def test_record_survives_readonly_root(tmp_path: Path) -> None:
    blocked = tmp_path / "blocked"  # file where a dir is needed
    blocked.write_text("x")
    record(blocked / "inside", verb="v", detail_level="normal", payload_bytes=1)  # no raise


def test_report_aggregates_and_computes_effect(tmp_path: Path) -> None:
    record(tmp_path, verb="analyze", detail_level="summary", payload_bytes=200)
    record(tmp_path, verb="analyze", detail_level="normal", payload_bytes=900)
    record(tmp_path, verb="rules list", detail_level="normal", payload_bytes=300)
    rep = report(tmp_path)
    assert rep["calls"] == 3
    assert rep["payload_bytes"] == 1400
    assert rep["by_verb"]["analyze"]["calls"] == 2
    assert rep["by_level"]["normal"]["payload_bytes"] == 1200
    effect = rep["detail_level_effect"]["analyze"]
    assert effect == {"summary_bytes": 200, "normal_bytes": 900, "saved_bytes": 700}
    assert "rules list" not in rep["detail_level_effect"]  # only seen at one level
    assert rep["tokens_unresolved"] is True


def test_report_empty_ledger(tmp_path: Path) -> None:
    rep = report(tmp_path)
    assert rep["calls"] == 0
    assert rep["detail_level_effect"] == {}
