"""Graph-database projections of the system graph: Gremlin CSV and N-Triples (AT-013/014)."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest

from apiforge.application.analyze import analyze_project
from apiforge.contracts.graph import GraphExport
from apiforge.graph import formats
from apiforge.graph.build import build_graph
from apiforge.graph.export import export_graph

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


@pytest.fixture
def built(tmp_path: Path) -> tuple[Path, GraphExport]:
    case_dir = tmp_path / "case"
    analyze_project(
        FIXTURES / "openapi" / "orders-v1.yaml", FIXTURES / "fastapi_orders", None, case_dir
    )
    out = tmp_path / "graph"
    return out, build_graph(case_dir, out)


def test_neptune_csv_round_trip(built: tuple[Path, GraphExport], tmp_path: Path) -> None:
    out = tmp_path / "nep"
    export = export_graph(built[0], out, fmt="neptune")
    vertices = (out / "vertices.csv").read_text(encoding="utf-8")
    edges = (out / "edges.csv").read_text(encoding="utf-8")
    assert formats.validate_gremlin_csv(vertices, edges) == []
    vrows = list(csv.reader(io.StringIO(vertices)))
    erows = list(csv.reader(io.StringIO(edges)))
    assert len(vrows) - 1 == export.node_count == built[1].node_count
    assert len(erows) - 1 == export.edge_count == built[1].edge_count
    assert all(column.endswith(":String") for column in vrows[0][2:])
    assert {name for name, _ in export.files} == {"vertices.csv", "edges.csv"}
    manifest = json.loads((out / "export.json").read_text(encoding="utf-8"))
    assert manifest["format"] == "neptune"


def test_neptune_csv_is_deterministic(built: tuple[Path, GraphExport], tmp_path: Path) -> None:
    first = export_graph(built[0], tmp_path / "a", fmt="neptune")
    second = export_graph(built[0], tmp_path / "b", fmt="neptune")
    assert first.files == second.files


def test_rdf_round_trip(built: tuple[Path, GraphExport], tmp_path: Path) -> None:
    out = tmp_path / "rdf"
    export = export_graph(built[0], out, fmt="rdf")
    text = (out / "graph.nt").read_text(encoding="utf-8")
    assert formats.validate_ntriples(text) == []
    nodes = formats.read_jsonl(built[0] / "nodes.jsonl")
    edges = formats.read_jsonl(built[0] / "edges.jsonl")
    props = sum(len(node.get("props") or {}) for node in nodes)
    distinct_edges = {(e["from_id"], e["kind"], e["to_id"]) for e in edges}
    assert len(text.splitlines()) == len(nodes) + props + len(distinct_edges)
    assert export.format == "rdf"


def test_validators_reject_broken_projections() -> None:
    assert formats.validate_gremlin_csv("id,label\n", "~id,~from,~to,~label\ne1,a,b,x\n")
    assert formats.validate_ntriples('<urn:a> <urn:b> "unterminated .\n')


def test_literals_are_escaped() -> None:
    text = formats.ntriples([{"id": "n 1", "kind": "fact", "props": {"q": 'say "hi"\n'}}], [])
    assert formats.validate_ntriples(text) == []
    assert "urn:apiforge:node:n%201" in text
