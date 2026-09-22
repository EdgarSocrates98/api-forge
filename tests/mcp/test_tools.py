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
        "graph_query",
        "graph_impact",
        "graph_trace",
        "graph_coverage",
        "index_status",
        "task_status",
        "brief_show",
        "contract_list",
        "contract_show",
        "model_dump",
        "model_redis",
        "model_otel",
        "perf_compare",
        "autonomy_status",
        "knowledge_list",
        "knowledge_show",
        "knowledge_check",
    }


def test_new_read_tools_mirror_cli(tmp_path: Path) -> None:
    """graph/index/task/brief/contract tools return the CLI-shaped payloads."""
    from apiforge.application.analyze import analyze_project
    from apiforge.contracts.task import TaskSpec
    from apiforge.graph.build import build_graph
    from apiforge.index.build import build_index
    from apiforge.taskspec.service import create_task

    case_dir = tmp_path / "case"
    analyze_project(CONTRACT, PROJECT, None, case_dir)
    graph_dir = tmp_path / "graph"
    build_graph(case_dir, graph_dir)

    assert tools.graph_coverage(str(graph_dir))["counts"]["finding"] > 0
    q = tools.graph_query(str(graph_dir), kind="finding")
    assert q["node_count"] > 0
    backed = next(
        json.loads(line)
        for line in (graph_dir / "edges.jsonl").read_text().splitlines()
        if line.strip() and json.loads(line)["kind"] == "backed_by"
    )
    tr = tools.graph_trace(str(graph_dir), backed["from_id"], backed["to_id"])
    assert tr["reachable"] is True
    im = tools.graph_impact(str(graph_dir), backed["to_id"])
    assert im["impacted_count"] >= 1

    build_index(PROJECT, tmp_path)
    st = tools.index_status(str(PROJECT), str(tmp_path))
    assert st["stale"] is False

    create_task(tmp_path, TaskSpec.model_validate({"id": "mcp-1", "outcome": "x"}))
    ts = tools.task_status("mcp-1", str(tmp_path))
    assert ts["task"]["id"] == "mcp-1"
    br = tools.brief_show("mcp-1", str(tmp_path))
    assert br["status"] in {"DECIDE", "REVIEW", "BLOCKED", "FAILED", "DONE"}
    assert "OutcomeBrief/v1" in tools.contract_list()["contracts"]
    assert tools.contract_show("OutcomeBrief/v1")["title"]


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
