"""Graphify nativo: canonical store, build from case, closed queries."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.application.analyze import analyze_project
from apiforge.contracts.base import ContractError
from apiforge.contracts.graph import GraphExport
from apiforge.graph.build import build_graph
from apiforge.graph.export import export_graph
from apiforge.graph.query import coverage, impact, query_graph, trace
from apiforge.graph.store import read_graph

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


@pytest.fixture
def built(tmp_path: Path) -> tuple[Path, GraphExport]:
    case_dir = tmp_path / "case"
    analyze_project(
        FIXTURES / "openapi" / "orders-v1.yaml",
        FIXTURES / "fastapi_orders",
        None,
        case_dir,
    )
    out = tmp_path / "graph"
    return out, build_graph(case_dir, out)


def test_build_emits_nodes_and_edges(built: tuple[Path, GraphExport]) -> None:
    out, export = built
    assert export.node_count > 0
    assert export.edge_count > 0
    nodes, edges = read_graph(out)
    kinds = {n.kind.value for n in nodes}
    assert {"case", "fact", "finding", "operation", "rule"} <= kinds
    edge_kinds = {e.kind.value for e in edges}
    assert "backed_by" in edge_kinds
    assert "violates" in edge_kinds


def test_build_is_deterministic(built: tuple[Path, GraphExport], tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    out2 = tmp_path / "graph2"
    export2 = build_graph(case_dir, out2)
    assert built[1].nodes_sha256 == export2.nodes_sha256
    assert built[1].edges_sha256 == export2.edges_sha256
    out1 = built[0]
    assert (out1 / "nodes.jsonl").read_bytes() == (out2 / "nodes.jsonl").read_bytes()


def test_query_filters_by_kind(built: tuple[Path, GraphExport]) -> None:
    result = query_graph(built[0], kind="finding")
    assert result["node_count"] > 0
    assert all(n["kind"] == "finding" for n in result["nodes"])
    edges = query_graph(built[0], edge_kind="backed_by")
    assert all(e["kind"] == "backed_by" for e in edges["edges"])


def test_query_rejects_unknown_kind(built: tuple[Path, GraphExport]) -> None:
    with pytest.raises(ContractError, match="AF-GRAPH-KIND"):
        query_graph(built[0], kind="nonsense")


def test_impact_names_dependents(built: tuple[Path, GraphExport]) -> None:
    _, edges = read_graph(built[0])
    backed = next(e for e in edges if e.kind.value == "backed_by")
    result = impact(built[0], backed.to_id)
    ids = {i["id"] for i in result["impacted"]}
    assert backed.from_id in ids


def test_trace_finding_to_fact(built: tuple[Path, GraphExport]) -> None:
    _, edges = read_graph(built[0])
    backed = next(e for e in edges if e.kind.value == "backed_by")
    result = trace(built[0], backed.from_id, backed.to_id)
    assert result["reachable"] is True
    assert result["path"][0]["kind"] == "backed_by"


def test_trace_unreachable_is_named(built: tuple[Path, GraphExport]) -> None:
    nodes, _ = read_graph(built[0])
    case_node = next(n for n in nodes if n.kind.value == "case")
    fact_node = next(n for n in nodes if n.kind.value == "fact")
    result = trace(built[0], case_node.id, fact_node.id)
    assert result["reachable"] is False


def test_coverage_names_gaps(built: tuple[Path, GraphExport]) -> None:
    report = coverage(built[0])
    assert report["counts"]["finding"] > 0
    assert isinstance(report["findings_unverified"], list)
    assert isinstance(report["operations_unimplemented"], list)


def test_export_copies_canonical_bytes(built: tuple[Path, GraphExport], tmp_path: Path) -> None:
    out = tmp_path / "export"
    export = export_graph(built[0], out)
    assert export.nodes_sha256 == built[1].nodes_sha256
    assert (out / "nodes.jsonl").read_bytes() == (built[0] / "nodes.jsonl").read_bytes()
    assert (out / "export.json").is_file()


def test_export_neptune_is_named_stub(built: tuple[Path, GraphExport], tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-GRAPH-FORMAT"):
        export_graph(built[0], tmp_path / "nep", fmt="neptune")


def test_tampered_node_line_refuses(built: tuple[Path, GraphExport]) -> None:
    path = built[0] / "nodes.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    row = json.loads(lines[0])
    row["props"]["injected"] = True
    lines[0] = json.dumps(row, sort_keys=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-GRAPH-HASH-MISMATCH"):
        read_graph(built[0])


def test_missing_graph_refuses(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-GRAPH-NOT-FOUND"):
        read_graph(tmp_path)
    with pytest.raises(ContractError, match="AF-GRAPH-NO-CASE"):
        build_graph(tmp_path / "nope", tmp_path / "g")


def test_tasks_become_nodes(tmp_path: Path) -> None:
    from apiforge.contracts.task import TaskSpec
    from apiforge.taskspec.service import create_task

    case_dir = tmp_path / "case"
    analyze_project(
        FIXTURES / "openapi" / "orders-v1.yaml",
        FIXTURES / "fastapi_orders",
        None,
        case_dir,
    )
    root = tmp_path / "root"
    create_task(root, TaskSpec.model_validate({"id": "t-9", "outcome": "x"}))
    out = tmp_path / "graph"
    build_graph(case_dir, out, tasks_root=root)
    result = query_graph(out, kind="task")
    assert result["node_count"] == 1
    assert result["nodes"][0]["id"] == "task:t-9"
