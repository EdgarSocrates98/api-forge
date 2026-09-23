from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.application.change_control import run_change_control
from apiforge.cli import app
from apiforge.core.io import sha256_file
from apiforge.integrations.replay import ReplayAdapter

runner = CliRunner()


def test_change_control_flow(tmp_path: Path) -> None:
    bundle_path = Path("tests/fixtures/api_git_cicd/change_bundle.json")
    bundle = ReplayAdapter().load(bundle_path)
    run_dir = tmp_path / "run"
    first = run_change_control(bundle, run_dir)
    first_hashes = {
        name: sha256_file(run_dir / name)
        for name in (
            "case/case.json",
            "case/facts.json",
            "case/findings.json",
            "graph/nodes.jsonl",
            "graph/edges.jsonl",
            "evidence/receipt.json",
        )
    }
    second = run_change_control(bundle, run_dir)
    second_hashes = {name: sha256_file(run_dir / name) for name in first_hashes}
    assert first.status == second.status == "review"
    assert first.payload["analysis"]["case_id"] == second.payload["analysis"]["case_id"]
    assert first.payload["route"] == second.payload["route"]
    assert first_hashes == second_hashes
    assert json.loads((run_dir / "brief.json").read_text())["status"] == "REVIEW"


def test_change_control_cli_has_no_traceback_on_malformed_bundle(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not-json", encoding="utf-8")
    result = runner.invoke(app, ["change-control", "run", "--bundle", str(bad)])
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "AF-CLI-INPUT" in result.output


def test_github_collect_without_token_is_governed(monkeypatch) -> None:
    monkeypatch.delenv("APIFORGE_GITHUB_READ_ONLY_TOKEN", raising=False)
    result = runner.invoke(
        app,
        [
            "change-control",
            "collect",
            "--repository",
            "example/repo",
            "--base-sha",
            "0" * 40,
            "--head-sha",
            "1" * 40,
        ],
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "AF-GITHUB-AUTH" in result.output
