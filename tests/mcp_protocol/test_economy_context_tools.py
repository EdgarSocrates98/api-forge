import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.mcp import tools
from tests.context.gateway_support import analyzed_root

runner = CliRunner()


@pytest.fixture(scope="module")
def root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return analyzed_root(tmp_path_factory.mktemp("parity"), "fastapi")


def _cli(*args: str) -> dict[str, object]:
    result = runner.invoke(app, list(args))
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_capsule_payload_is_identical_on_cli_and_mcp(root: Path, monkeypatch) -> None:
    monkeypatch.chdir(root)
    cli = _cli("context", "capsule", "--target", "GET /payments/{payment_id}", "--root", str(root))
    mcp = tools.context_capsule("GET /payments/{payment_id}", root=str(root))
    assert cli == mcp
    assert cli["schema"] == "apiforge/context-capsule/v1"
    legacy = [
        json.loads(line)
        for line in (root / ".apiforge" / "economy.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert any(row["verb"] == "mcp:context_capsule" and row["payload_bytes"] > 0 for row in legacy)


def test_expand_stats_and_explain_round_trip(root: Path, monkeypatch) -> None:
    monkeypatch.chdir(root)
    capsule = tools.context_capsule("GET /payments/{payment_id}", root=str(root))
    uri = capsule["refs"][0]["uri"]
    expanded = tools.context_expand(uri, root=str(root), run_id=capsule["run_id"])
    assert expanded["verified"] is True
    assert _cli("context", "expand", uri, "--root", str(root))["content"] == expanded["content"]
    stats = tools.economy_stats(root=str(root), run_id=capsule["run_id"])
    assert stats["tokens_unresolved"] is True
    assert "envelope" in stats["by_source"]
    explained = _cli("economy", "explain", capsule["run_id"], "--root", str(root))
    assert explained == tools.economy_explain(capsule["run_id"], root=str(root))


def test_cli_refusals_keep_code_field_and_unlock(root: Path) -> None:
    result = runner.invoke(
        app, ["context", "expand", "ctx://sha256/" + "0" * 64, "--root", str(root)]
    )
    assert result.exit_code == 2
    assert "AF-CTX-REF-NOT-FOUND" in result.output
    assert "field=uri" in result.output
    assert "unlock=" in result.output


def test_degraded_capsule_exits_zero_with_explicit_status(tmp_path: Path) -> None:
    payload = _cli("context", "capsule", "--target", "POST /orders", "--root", str(tmp_path))
    assert payload["status"] == "degraded"
    assert payload["refusals"][0]["code"] == "AF-CTX-GRAPH-UNAVAILABLE"
