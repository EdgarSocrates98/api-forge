"""Closed-vocabulary graph queries over the canonical JSONL store."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.graph import EdgeKind, GraphEdge, NodeKind
from apiforge.graph.store import edge_line, node_line, read_graph


def query_graph(
    graph_dir: Path,
    kind: str | None = None,
    edge_kind: str | None = None,
    prop: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Filter nodes/edges by closed vocabulary. `prop` entries are `k=v`."""
    nodes, edges = read_graph(graph_dir)
    if kind is not None:
        try:
            wanted = NodeKind(kind)
        except ValueError as exc:
            raise ContractError(
                "AF-GRAPH-KIND", f"unknown node kind {kind!r}"
            ) from exc
        nodes = [n for n in nodes if n.kind is wanted]
    filters = dict(p.split("=", 1) for p in prop)
    for key, value in filters.items():
        nodes = [n for n in nodes if str(n.props.get(key)) == value]
    if edge_kind is not None:
        try:
            wanted_edge = EdgeKind(edge_kind)
        except ValueError as exc:
            raise ContractError(
                "AF-GRAPH-KIND", f"unknown edge kind {edge_kind!r}"
            ) from exc
        edges = [e for e in edges if e.kind is wanted_edge]
    return {
        "nodes": [node_line(n) for n in nodes],
        "edges": [edge_line(e) for e in edges],
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


def _adjacency(
    edges: list[GraphEdge], reverse: bool
) -> dict[str, list[tuple[str, str]]]:
    adj: dict[str, list[tuple[str, str]]] = {}
    for e in edges:
        src, dst = (e.to_id, e.from_id) if reverse else (e.from_id, e.to_id)
        adj.setdefault(src, []).append((dst, e.kind.value))
    for value in adj.values():
        value.sort()
    return adj


def impact(graph_dir: Path, node_id: str, max_depth: int = 4) -> dict[str, Any]:
    """Everything that transitively depends on `node_id` (reverse traversal)."""
    nodes, edges = read_graph(graph_dir)
    known = {n.id for n in nodes}
    if node_id not in known:
        raise ContractError("AF-GRAPH-NODE", f"no node {node_id!r} in the graph")
    adj = _adjacency(edges, reverse=True)
    seen: dict[str, int] = {}
    queue: deque[tuple[str, int]] = deque([(node_id, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for nxt, kind in adj.get(current, []):
            if nxt not in seen and nxt != node_id:
                seen[nxt] = depth + 1
                queue.append((nxt, depth + 1))
    return {
        "node": node_id,
        "impacted": [{"id": k, "depth": v} for k, v in sorted(seen.items())],
        "impacted_count": len(seen),
    }


def trace(graph_dir: Path, from_id: str, to_id: str) -> dict[str, Any]:
    """Shortest directed path `from_id` -> `to_id`; absent path is named."""
    nodes, edges = read_graph(graph_dir)
    known = {n.id for n in nodes}
    for nid in (from_id, to_id):
        if nid not in known:
            raise ContractError("AF-GRAPH-NODE", f"no node {nid!r} in the graph")
    adj = _adjacency(edges, reverse=False)
    prev: dict[str, tuple[str, str]] = {}
    queue: deque[str] = deque([from_id])
    seen = {from_id}
    while queue:
        current = queue.popleft()
        if current == to_id:
            break
        for nxt, kind in adj.get(current, []):
            if nxt not in seen:
                seen.add(nxt)
                prev[nxt] = (current, kind)
                queue.append(nxt)
    if to_id not in seen:
        return {"from": from_id, "to": to_id, "path": [], "reachable": False}
    hops: list[dict[str, str]] = []
    node = to_id
    while node != from_id:
        parent, kind = prev[node]
        hops.append({"from": parent, "to": node, "kind": kind})
        node = parent
    hops.reverse()
    return {"from": from_id, "to": to_id, "path": hops, "reachable": True}


def coverage(graph_dir: Path) -> dict[str, Any]:
    """Structural gaps: findings without verified_by, ops without impl, etc."""
    nodes, edges = read_graph(graph_dir)
    counts: dict[str, int] = {}
    for n in nodes:
        counts[n.kind.value] = counts.get(n.kind.value, 0) + 1
    verified = {e.from_id for e in edges if e.kind is EdgeKind.VERIFIED_BY}
    implemented = {e.from_id for e in edges if e.kind is EdgeKind.IMPLEMENTED_BY}
    backed = {e.to_id for e in edges if e.kind is EdgeKind.BACKED_BY}
    findings = [n.id for n in nodes if n.kind is NodeKind.FINDING]
    ops = [n.id for n in nodes if n.kind is NodeKind.OPERATION]
    facts = [n.id for n in nodes if n.kind is NodeKind.FACT]
    return {
        "counts": counts,
        "findings_unverified": sorted(f for f in findings if f not in verified),
        "operations_unimplemented": sorted(o for o in ops if o not in implemented),
        "facts_unreferenced": sorted(f for f in facts if f not in backed),
    }
