"""MCP tool bodies: same payloads as the CLI, economy recorded as mcp:<verb>."""

import json
from pathlib import Path

import pytest

from apiforge.mcp import tools

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
CONTRACT = FIXTURES / "openapi" / "orders-v1.yaml"
PROJECT = FIXTURES / "fastapi_orders"


def test_tools_export_all_expected_verbs() -> None:
    names = {t.__name__ for t in tools.TOOLS}
    assert names == {
        "discover",
        "analyze",
        "judge",
        "model_build",
        "model_api_gateway",
        "diff_contract",
        "next_step",
        "rules_list",
        "rules_lookup",
        "playbook",
        "economy_report",
        "context_funnel",
    }


def test_rules_lookup_payload_and_economy(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    data = tools.rules_lookup("AF-SEC-001")
    assert data["id"] == "AF-SEC-001"
    ledger = tmp_path / ".apiforge" / "economy.jsonl"
    entry = json.loads(ledger.read_text().strip().splitlines()[-1])
    assert entry["verb"] == "mcp:rules_lookup"


def test_playbook_unknown_refuses() -> None:
    from apiforge.application.analyze import AnalysisError

    with pytest.raises(AnalysisError, match="AF-PLAYBOOK-NOT-FOUND"):
        tools.playbook("nobody")


def test_analyze_persists_case(tmp_path: Path) -> None:
    out = tmp_path / "case"
    data = tools.analyze(str(CONTRACT), str(PROJECT), out_dir=str(out))
    assert data["operations"] > 0
    assert (out / "case.json").is_file()


def test_server_imports_or_refuses() -> None:
    """build_server works when the mcp extra is installed; otherwise ImportError."""
    try:
        from apiforge.mcp.server import build_server

        server = build_server()
        assert server is not None
    except ImportError:
        pytest.skip("mcp extra not installed")
