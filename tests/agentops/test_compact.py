from pathlib import Path

import pytest

from apiforge.agentops.compact import CavemanMode, compact_file, compact_text
from apiforge.agentops.evals import evaluate_compaction
from apiforge.agentops.filters import apply_filter, get_filter
from apiforge.agentops.hosts import list_hosts
from apiforge.agentops.workflows import plan_workflow


def test_compaction_preserves_critical_error_and_provenance() -> None:
    output = "\n".join(
        ["progress 1", "noise 2", "ERROR AF-DB-TIMEOUT", *[f"noise {i}" for i in range(20)]]
    )
    result = compact_text(output, command="pytest", mode=CavemanMode.ULTRA, max_lines=5)

    assert "ERROR AF-DB-TIMEOUT" in result.text
    assert result.critical_evidence_preserved is True
    assert result.omitted_lines > 0
    assert result.source_sha256
    assert result.emitted_bytes < result.original_bytes


def test_off_mode_keeps_semantic_lines_without_compaction() -> None:
    result = compact_text("one\ntwo\n", mode="off")

    assert result.omitted_lines == 0
    assert result.text == "one\ntwo\n"
    assert result.critical_evidence_preserved is True


def test_invalid_limit_refused() -> None:
    with pytest.raises(ValueError, match="AF-COMPACT-LIMIT"):
        compact_text("x", max_lines=0)


def test_file_mode_is_read_only(tmp_path: Path) -> None:
    path = tmp_path / "tool.log"
    original = "WARNING: keep\n" + "noise\n" * 100
    path.write_text(original, encoding="utf-8")

    result = compact_file(path, command="tool", max_lines=5)

    assert path.read_text(encoding="utf-8") == original
    assert result.artifact == str(path)


def test_context_compact_cli_is_offline_and_json(tmp_path: Path) -> None:
    from typer.testing import CliRunner

    from apiforge.cli import app

    path = tmp_path / "tool.log"
    path.write_text("noise\nERROR AF-CLI-FAILED\n" + "tail\n" * 30, encoding="utf-8")
    result = CliRunner().invoke(
        app,
        ["context", "compact", "--input", str(path), "--mode", "ultra", "--max-lines", "4"],
    )

    assert result.exit_code == 0, result.output
    assert '"critical_evidence_preserved": true' in result.output
    assert "AF-CLI-FAILED" in result.output


def test_declared_command_filter_is_deterministic() -> None:
    text = "[INFO] --- maven-plugin ---\nDownloading from repo\nERROR AF-MVN-FAILED\n"
    assert get_filter("mvn test") is not None
    assert "ERROR AF-MVN-FAILED" in apply_filter(text, "mvn test")
    assert "Downloading" not in apply_filter(text, "mvn test")


def test_cli_compaction_is_recorded_in_economy_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from typer.testing import CliRunner

    from apiforge.cli import app

    path = tmp_path / "tool.log"
    path.write_text("noise\n" * 100, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app, ["context", "compact", "--input", str(path), "--max-lines", "5"]
    )

    assert result.exit_code == 0, result.output
    ledger = tmp_path / ".apiforge" / "economy.jsonl"
    assert ledger.is_file()
    assert '"source_bytes"' in ledger.read_text(encoding="utf-8")


def test_workflow_and_host_adapters_are_closed_and_local() -> None:
    plan = plan_workflow("migration")
    assert "holdout" in plan.required_evidence
    assert plan.mutation_allowed is False
    assert {item["name"] for item in list_hosts()} == {"claude", "gpt-codex", "devin", "copilot"}


def test_compaction_eval_detects_critical_loss() -> None:
    result = compact_text("ERROR AF-KEEP\n" + "noise\n" * 50, max_lines=2)
    evaluation = evaluate_compaction("ERROR AF-KEEP\n" + "noise\n" * 50, result)
    assert evaluation["passed"] is True
