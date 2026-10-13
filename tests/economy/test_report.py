"""E2E: `apiforge economy report` aggregates the recorded call sizes."""

import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.economy.ledger import record

runner = CliRunner()


def test_economy_report_reads_ledger(tmp_path: Path) -> None:
    record(tmp_path, verb="apiforge rules list", detail_level="normal", payload_bytes=500)
    record(tmp_path, verb="apiforge rules list", detail_level="summary", payload_bytes=150)
    result = runner.invoke(app, ["economy", "report", "--root", str(tmp_path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["calls"] == 2
    assert data["payload_bytes"] == 650
    assert data["detail_level_effect"]["apiforge rules list"]["saved_bytes"] == 350
    assert data["tokens_unresolved"] is True


def test_calls_are_recorded_to_cwd_ledger(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    ledger = tmp_path / ".apiforge" / "economy.jsonl"
    assert ledger.is_file()
    entry = json.loads(ledger.read_text().strip())
    assert entry["verb"].endswith("rules list")
    assert entry["detail_level"] == "normal"
    assert entry["payload_bytes"] > 0
