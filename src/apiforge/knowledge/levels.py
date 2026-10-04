"""§36 Adaptive Retrieval — L0 exact → L1 lexical → L2 graph → L3 hybrid
semantic → L4 reranker. Escalation happens only while the current level is
insufficient per declared thresholds; every step is recorded in ``steps``.

Levels are honest: L2 widens via document-structure edges (sibling sections
of L1 hits); L3 exists only when a semantic adapter is declared; L4 is a
deterministic weighted rerank over the accumulated candidates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.economy_extras import Passage
from apiforge.contracts.model_routing import (
    AdaptiveRetrievalResult,
    RetrievalLevel,
    RetrievalStep,
)
from apiforge.knowledge.retrieval import expand, normalize, search
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
    hits: tuple[Passage, ...], query: str, *, root: Path | None, store_root: Path | None
) -> tuple[Passage, ...]:
    """L2: structural edges — sibling sections of the hit documents."""
    siblings = list(hits)
    seen = {(item.pack_id, item.file, item.heading) for item in hits}
    anchor_docs = {(item.pack_id, item.file) for item in hits[:3]}
    for passage in _lexical(query, root=root, store_root=store_root):
        key = (passage.pack_id, passage.file, passage.heading)
        if key in seen:
            continue
        if (passage.pack_id, passage.file) in anchor_docs:
            siblings.append(passage)
            seen.add(key)
    return tuple(siblings)


def _hybrid(
    hits: tuple[Passage, ...],
    query: str,
    semantic: SemanticAdapter,
    weights: dict[str, float],
) -> tuple[Passage, ...]:
    """L3: lexical score blended with semantic similarity per candidate."""
    terms, _ = expand(query)
    top = max((item.score for item in hits), default=1.0) or 1.0
    rescored = sorted(
        hits,
        key=lambda item: (
            weights["lexical"] * (item.score / top)
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
    for index, level in enumerate(order[: ceiling + 1]):
        if level == "L0":
            hits = _exact(query, root=root, store_root=store_root)
        elif level == "L1":
            hits = _lexical(query, root=root, store_root=store_root)
        elif level == "L2":
            hits = _graph(hits, query, root=root, store_root=store_root)
        elif level == "L3":
            if semantic is None:
                unresolved.append("semantic")
                steps.append(
                    RetrievalStep(
                        level="L3", hits=len(hits), escalated=True, reason="adapter undeclared"
                    )
                )
                continue
            hits = _hybrid(hits, query, semantic, rules["hybrid"])
            semantic_used = True
        else:
            hits = _rerank(hits, query, semantic, rules["rerank"])
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
        unresolved=tuple(sorted(unresolved)),
    )


__all__ = ["adaptive_retrieve", "load_level_policy"]
