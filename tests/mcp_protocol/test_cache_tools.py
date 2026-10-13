import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.mcp import tools
from tests.context.gateway_support import analyzed_root

runner = CliRunner()
TARGET = "GET /customers/{customer_id}"


@pytest.fixture(scope="module")
def root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return analyzed_root(tmp_path_factory.mktemp("cache-parity"), "fastapi")


def _cli(*args: str) -> dict[str, object]:
    result = runner.invoke(app, list(args))
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_delta_and_stats_are_identical_on_cli_and_mcp(root: Path, monkeypatch) -> None:
    monkeypatch.chdir(root)
    tools.context_capsule(TARGET, root=str(root))
    changed = "proj/app/routes/customers.py"
    cli = _cli("context", "delta", "--changed", changed, "--root", str(root))
    assert cli == tools.context_delta(changed=[changed], root=str(root))
    assert cli["capsule_targets"] == [TARGET]
    stats = _cli("cache", "stats", "--root", str(root))
    assert stats == tools.cache_stats(root=str(root))
    assert stats["layers"]["capsule"]["entries"] >= 1


def test_no_cache_flag_keeps_capsule_bytes(root: Path, monkeypatch) -> None:
    monkeypatch.chdir(root)
    cached = _cli("context", "capsule", "--target", TARGET, "--root", str(root))
    uncached = _cli("context", "capsule", "--target", TARGET, "--root", str(root), "--no-cache")
    assert cached == uncached == tools.context_capsule(TARGET, root=str(root), no_cache=True)


def test_invalidate_and_gc_parity(root: Path, monkeypatch) -> None:
    monkeypatch.chdir(root)
    tools.context_capsule(TARGET, root=str(root))
    changed = "proj/app/routes/customers.py"
    dropped = _cli("cache", "invalidate", "--changed", changed, "--root", str(root))
    assert [item["subject"] for item in dropped["invalidated"]] == [TARGET]
    assert tools.cache_invalidate(changed=[changed], root=str(root))["invalidated"] == []
    report = _cli("context", "gc", "--root", str(root))
    assert report["applied"] is False
    assert report == tools.context_gc(root=str(root))


def test_cli_refusals_keep_code_field_and_unlock(root: Path) -> None:
    result = runner.invoke(app, ["context", "delta", "--root", str(root)])
    assert result.exit_code == 2
    assert "AF-DELTA-INPUT-MISSING" in result.output
    assert "field=base" in result.output and "unlock=" in result.output
    disabled = runner.invoke(app, ["cache", "stats", "--layer", "model_response"])
    assert disabled.exit_code == 2
    assert "AF-CACHE-LAYER-DISABLED" in disabled.output
