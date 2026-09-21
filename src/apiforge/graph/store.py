"""Canonical JSONL graph store: nodes.jsonl + edges.jsonl, sorted, hashed.

Each node line is ``{"id","kind","props","sha256"}`` where ``sha256`` covers
the canonical ``{"id","kind","props"}`` payload -- a tampered props value is
detectable line by line. Lines are sorted so identical inputs produce
identical bytes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.graph import EdgeKind, GraphEdge, GraphNode, NodeKind

NODES_FILE = "nodes.jsonl"
EDGES_FILE = "edges.jsonl"


def _canonical(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def node_sha256(node: GraphNode) -> str:
    payload = {"id": node.id, "kind": node.kind.value, "props": dict(node.props)}
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def node_line(node: GraphNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "kind": node.kind.value,
        "props": dict(node.props),
        "sha256": node.sha256 or node_sha256(node),
        "version": node.version,
    }


def edge_line(edge: GraphEdge) -> dict[str, Any]:
    return {
        "from_id": edge.from_id,
        "to_id": edge.to_id,
        "kind": edge.kind.value,
        "props": dict(edge.props),
        "version": edge.version,
    }


def write_graph(
    out_dir: Path, nodes: list[GraphNode], edges: list[GraphEdge]
) -> dict[str, Any]:
    """Write canonical node/edge files; return their digests and counts."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dedup_nodes = {node_line(n)["id"]: node_line(n) for n in nodes}
    node_rows = [dedup_nodes[k] for k in sorted(dedup_nodes)]
    seen_edges: set[tuple[str, str, str]] = set()
    edge_rows: list[dict[str, Any]] = []
    for e in sorted(edges, key=lambda e: (e.from_id, e.to_id, e.kind.value)):
        key = (e.from_id, e.to_id, e.kind.value)
        if key not in seen_edges:
            seen_edges.add(key)
            edge_rows.append(edge_line(e))
    nodes_text = "".join(_canonical(r) + "\n" for r in node_rows)
    edges_text = "".join(_canonical(r) + "\n" for r in edge_rows)
    (out / NODES_FILE).write_text(nodes_text, encoding="utf-8", newline="")
    (out / EDGES_FILE).write_text(edges_text, encoding="utf-8", newline="")
    return {
        "nodes_sha256": hashlib.sha256(nodes_text.encode("utf-8")).hexdigest(),
        "edges_sha256": hashlib.sha256(edges_text.encode("utf-8")).hexdigest(),
        "node_count": len(node_rows),
        "edge_count": len(edge_rows),
    }


def _parse_node(row: dict[str, Any], source: Path) -> GraphNode:
    try:
        return GraphNode.model_validate(row)
    except Exception as exc:
        raise ContractError("AF-GRAPH-INVALID", f"{source}: {exc}") from exc


def _parse_edge(row: dict[str, Any], source: Path) -> GraphEdge:
    try:
        return GraphEdge.model_validate(row)
    except Exception as exc:
        raise ContractError("AF-GRAPH-INVALID", f"{source}: {exc}") from exc


def read_graph(graph_dir: Path) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Load nodes+edges; verify each node line's sha256."""
    root = Path(graph_dir)
    nodes_path = root / NODES_FILE
    edges_path = root / EDGES_FILE
    if not nodes_path.is_file():
        raise ContractError("AF-GRAPH-NOT-FOUND", f"no {NODES_FILE} under {root}")
    nodes: list[GraphNode] = []
    for raw in nodes_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        node = _parse_node(row, nodes_path)
        if node.sha256 != node_sha256(node):
            raise ContractError(
                "AF-GRAPH-HASH-MISMATCH", f"node {node.id} sha256 diverges"
            )
        nodes.append(node)
    edges: list[GraphEdge] = []
    if edges_path.is_file():
        for raw in edges_path.read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            edges.append(_parse_edge(json.loads(raw), edges_path))
    return nodes, edges


__all__ = [
    "EdgeKind",
    "GraphEdge",
    "GraphNode",
    "NodeKind",
    "read_graph",
    "write_graph",
]
