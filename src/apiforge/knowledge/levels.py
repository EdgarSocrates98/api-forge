"""§36 Adaptive Retrieval — L0 exact → L1 lexical → L2 graph → L3 hybrid
semantic → L4 reranker. Escalation happens only while the current level is
insufficient per declared thresholds; every step is recorded in ``steps``.

Levels are honest: L2 traverses a declared bounded graph; L3 exists only when
a semantic adapter is declared; L4 is a deterministic weighted rerank over
the accumulated candidates.
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.economy_extras import Passage
from apiforge.contracts.graph import GraphNode
from apiforge.contracts.model_routing import (
    AdaptiveRetrievalResult,
    RetrievalLevel,
    RetrievalStep,
)
from apiforge.graph.store import read_graph
from apiforge.knowledge.retrieval import corpus_passages, expand, normalize, search
from apiforge.knowledge.semantic import SemanticAdapter

RULES = Path(__file__).resolve().parent.parent / "rules" / "retrieval_levels.yaml"


def load_level_policy(path: Path | None = None) -> dict[str, Any]:
    data = yaml.safe_load((path or RULES).read_text(encoding="utf-8")) or {}
    return {
        "levels": data.get("levels") or {},
        "hybrid": data.get("hybrid") or {"lexical": 0.6, "semantic": 0.4},
        "rerank": data.get("rerank") or {"lexical": 0.45, "graph": 0.25, "semantic": 0.30},
    }


def _sufficient(
    level: RetrievalLevel, hits: int, top: float | None, policy: dict[str, Any]
) -> bool:
    gate = policy["levels"].get(level) or {}
    return hits >= int(gate.get("min_hits", 1)) and (top or 0.0) >= float(
        gate.get("min_score", 0.0)
    )


def _exact(query: str, *, root: Path | None, store_root: Path | None) -> tuple[Passage, ...]:
    """L0: the query *is* an identifier (ctx ref, pack:file, heading match)."""
    normalized = normalize(query)
    if not normalized or " " in normalized:
        return ()
    result = search(query, tier=3, root=root, store_root=store_root)
    for passage in result.passages:
        if normalize(passage.heading) == normalized or normalize(passage.pack_id) == normalized:
            return (passage,)
    return ()


def _lexical(query: str, *, root: Path | None, store_root: Path | None) -> tuple[Passage, ...]:
    return tuple(search(query, tier=3, root=root, store_root=store_root).passages)


def _graph(
    hits: tuple[Passage, ...],
    query: str,
    *,
    root: Path | None,
    store_root: Path | None,
    graph_dir: Path,
    max_depth: int = 2,
    max_nodes: int = 32,
) -> tuple[Passage, ...]:
    """L2: bounded traversal over hashed graph nodes and edges."""
    from apiforge.context.gateway.refs import CtxStore

    nodes, edges = read_graph(graph_dir)
    terms, _ = expand(query)
    node_map = {node.id: node for node in nodes}

    def node_text(node: GraphNode) -> str:
        return normalize(" ".join((node.id, node.kind.value, json.dumps(dict(node.props)))))

    seeds = [node.id for node in nodes if any(term in node_text(node) for term in terms)]
    if not seeds and hits:
        seeds = [node.id for node in nodes if any(item.heading in node.id for item in hits)]
    adjacency: dict[str, set[str]] = {node.id: set() for node in nodes}
    for edge in edges:
        if edge.from_id in adjacency and edge.to_id in adjacency:
            adjacency[edge.from_id].add(edge.to_id)
            adjacency[edge.to_id].add(edge.from_id)
    queue = deque((seed, 0) for seed in sorted(set(seeds)))
    visited: dict[str, int] = {}
    while queue and len(visited) < max_nodes:
        node_id, depth = queue.popleft()
        if node_id in visited and visited[node_id] <= depth:
            continue
        visited[node_id] = depth
        if depth >= max_depth:
            continue
        for neighbor in sorted(adjacency.get(node_id, ())):
            queue.append((neighbor, depth + 1))

    store = CtxStore(Path(store_root or Path.cwd()))
    graph_hits = []
    for node_id, depth in sorted(visited.items(), key=lambda item: (item[1], item[0])):
        node = node_map[node_id]
        body = f"graph node {node.id} ({node.kind.value})\n{json.dumps(dict(node.props), sort_keys=True)}"
        graph_hits.append(
            Passage(
                pack_id="graph",
                file=str(graph_dir / "nodes.jsonl"),
                heading=node.id,
                score=1.0 / (depth + 1),
                signals={"graph_depth": float(depth)},
                ref=store.put(body),
                bytes=len(body.encode("utf-8")),
                provenance=(
                    "knowledge:graph",
                    f"graph:{graph_dir}",
                    f"node:{node.id}",
                    f"depth:{depth}",
                ),
            )
        )
    by_ref = {item.ref: item for item in graph_hits}
    by_ref.update({item.ref: item for item in hits if item.ref not in by_ref})
    return tuple(by_ref.values())


def _hybrid(
    hits: tuple[Passage, ...],
    query: str,
    semantic: SemanticAdapter,
    weights: dict[str, float],
    *,
    root: Path | None,
    store_root: Path | None,
) -> tuple[Passage, ...]:
    """L3: generate semantic candidates, then blend and rank both sources."""
    terms, _ = expand(query)
    lexical_refs = {item.ref for item in hits}
    corpus = corpus_passages(root=root, store_root=store_root)
    documents = tuple((item.ref, item.heading) for item in corpus)
    candidate_fn = getattr(semantic, "candidates", None)
    semantic_rows = candidate_fn(terms, documents) if callable(candidate_fn) else ()
    by_ref = {item.ref: item for item in hits}
    for ref, score in semantic_rows:
        if ref not in by_ref:
            item = next((candidate for candidate in corpus if candidate.ref == ref), None)
            if item is not None:
                by_ref[ref] = item.model_copy(
                    update={"signals": {**item.signals, "semantic_score": score}}
                )
    merged = tuple(by_ref.values())
    top = max((item.score for item in hits), default=1.0) or 1.0
    rescored = sorted(
        merged,
        key=lambda item: (
            weights["lexical"] * (item.score / top if item.ref in lexical_refs else 0.0)
            + weights["semantic"] * semantic.score(terms, item.heading)
        ),
        reverse=True,
    )
    return tuple(rescored)


def _rerank(
    hits: tuple[Passage, ...],
    query: str,
    semantic: SemanticAdapter | None,
    weights: dict[str, float],
) -> tuple[Passage, ...]:
    """L4: deterministic rerank over all accumulated signals."""
    terms, _ = expand(query)
    top = max((item.score for item in hits), default=1.0) or 1.0

    def score(item: Passage) -> float:
        graph_bonus = 1.0 if item.signals.get("selected_pack") else 0.0
        semantic_score = semantic.score(terms, item.heading) if semantic else 0.0
        return (
            weights["lexical"] * (item.score / top)
            + weights["graph"] * graph_bonus
            + weights["semantic"] * semantic_score
        )

    return tuple(sorted(hits, key=score, reverse=True))


def adaptive_retrieve(
    query: str,
    *,
    root: Path | None = None,
    store_root: Path | None = None,
    graph_dir: Path | None = None,
    semantic: SemanticAdapter | None = None,
    max_level: RetrievalLevel = "L4",
    policy: dict[str, Any] | None = None,
) -> AdaptiveRetrievalResult:
    """Run the §36 ladder until a level is sufficient — never higher."""
    rules = policy or load_level_policy()
    order: tuple[RetrievalLevel, ...] = ("L0", "L1", "L2", "L3", "L4")
    ceiling = order.index(max_level)
    steps: list[RetrievalStep] = []
    unresolved: list[str] = []
    hits: tuple[Passage, ...] = ()
    used: RetrievalLevel = "L0"
    semantic_used = False
    provenance: dict[str, tuple[str, ...]] = {}
    for index, level in enumerate(order[: ceiling + 1]):
        if level == "L0":
            hits = _exact(query, root=root, store_root=store_root)
        elif level == "L1":
            hits = _lexical(query, root=root, store_root=store_root)
        elif level == "L2":
            if graph_dir is None:
                unresolved.append("graph")
                steps.append(
                    RetrievalStep(
                        level="L2", hits=len(hits), escalated=True, reason="graph undeclared"
                    )
                )
                continue
            hits = _graph(
                hits,
                query,
                root=root,
                store_root=store_root,
                graph_dir=graph_dir,
            )
        elif level == "L3":
            if semantic is None:
                unresolved.append("semantic")
                steps.append(
                    RetrievalStep(
                        level="L3", hits=len(hits), escalated=True, reason="adapter undeclared"
                    )
                )
                continue
            hits = _hybrid(
                hits,
                query,
                semantic,
                rules["hybrid"],
                root=root,
                store_root=store_root,
            )
            semantic_used = True
        else:
            hits = _rerank(hits, query, semantic, rules["rerank"])
        provenance = {item.ref: item.provenance for item in hits[:5]}
        top = max((item.score for item in hits), default=None)
        sufficient = _sufficient(level, len(hits), top, rules)
        steps.append(
            RetrievalStep(
                level=level,
                hits=len(hits),
                top_score=top,
                escalated=not sufficient,
                reason="sufficient" if sufficient else "insufficient",
            )
        )
        used = level
        if sufficient or index == ceiling:
            break
    if not hits and "semantic" not in unresolved:
        unresolved.append("no-passage-matched")
    return AdaptiveRetrievalResult(
        query=query,
        level_used=used,
        steps=tuple(steps),
        hits=tuple(item.ref for item in hits[:5]),
        semantic_available=semantic_used,
        provenance=provenance,
        unresolved=tuple(sorted(unresolved)),
    )


__all__ = ["adaptive_retrieve", "load_level_policy"]
