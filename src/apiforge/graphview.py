"""API Forge → ForgeGraphView/v1 adapter.

Projects the canonical JSONL graph store (``graph build`` output) onto
the view contract. The store stays authoritative — every node line is
sha256-verified by ``read_graph`` before it is viewed.
"""

from __future__ import annotations

from pathlib import Path

from apiforge._graphview import (
    ForgeGraphView,
    GraphEdgeView,
    GraphNodeView,
    new_descriptor,
)

PROVIDER = "api-forge"


def build_view(graph_dir: str | Path) -> ForgeGraphView | None:
    """nodes.jsonl/edges.jsonl → view. None when the store is absent."""
    from apiforge.graph.store import read_graph

    try:
        nodes, edges = read_graph(Path(graph_dir))
    except Exception:
        return None
    desc = new_descriptor(
        provider_id=PROVIDER,
        domain="api",
        graph_id="api-graph",
        capabilities=(
            "node_inspect",
            "edge_inspect",
            "neighbors",
            "paths",
            "dependency_traversal",
            "impact_analysis",
            "search",
            "filter",
            "export",
        ),
        limitations=("epistemic state is declared: the store records extracted evidence",),
    )
    object.__setattr__(desc, "node_count", len(nodes))
    object.__setattr__(desc, "edge_count", len(edges))
    object.__setattr__(
        desc, "available_layers", tuple(sorted({n.kind.value for n in nodes}))
    )
    vnode = tuple(
        GraphNodeView(
            id=n.id,
            kind=n.kind.value,
            label=n.id,
            domain="api",
            source_provider=PROVIDER,
            attributes=dict(n.props),
            epistemic_state="declared",
            evidence_refs=(n.sha256,) if n.sha256 else (),
        )
        for n in nodes
    )
    vedge = tuple(
        GraphEdgeView(
            id=f"{e.from_id}|{e.kind.value}|{e.to_id}",
            source=e.from_id,
            target=e.to_id,
            kind=e.kind.value,
            provenance="declared",
            epistemic_state="declared",
            attributes=dict(e.props),
        )
        for e in edges
    )
    return ForgeGraphView(descriptor=desc, nodes=vnode, edges=vedge)
