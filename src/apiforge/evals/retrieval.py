"""§38 retrieval evals: lexical/graph/semantic/hybrid vs a gold corpus.

Metrics per strategy: recall (gold covered), precision (gold inside hits),
latency_ms (measured wall clock), tokens (bytes of returned passages / 4),
cost (tokens × the declared rate, or unresolved when no rate is declared).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_extras import Passage
from apiforge.contracts.model_routing import RetrievalComparison
from apiforge.knowledge.levels import _graph, _hybrid, _lexical, _rerank, load_level_policy
from apiforge.knowledge.semantic import HashEmbeddingAdapter

_STRATEGIES = ("lexical", "graph", "semantic", "hybrid")


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError("AF-EVALS-INVALID", f"retrieval corpus {corpus} empty or duplicated")
    return cases


def _strategy(
    name: str,
    query: str,
    semantic: HashEmbeddingAdapter | None,
    weights: dict[str, float],
    rerank: dict[str, float],
    root: Path | None,
) -> tuple[Passage, ...]:
    if name == "lexical":
        return _lexical(query, root=root, store_root=None)
    hits = _lexical(query, root=root, store_root=None)
    if name == "graph":
        return _graph(hits, query, root=root, store_root=None)
    if name == "semantic":
        adapter = semantic or HashEmbeddingAdapter()
        return _hybrid(hits, query, adapter, weights, root=root, store_root=None)
    adapter = semantic or HashEmbeddingAdapter()
    return _rerank(hits, query, adapter, rerank)


def _measure(
    name: str,
    query: str,
    gold: set[str],
    semantic: HashEmbeddingAdapter | None,
    weights: dict[str, float],
    rerank: dict[str, float],
    root: Path | None,
    cost_rate: float | None,
) -> RetrievalComparison:
    started = time.perf_counter()
    hits = _strategy(name, query, semantic, weights, rerank, root)[:5]
    latency_ms = (time.perf_counter() - started) * 1000
    keys = {item.heading for item in hits} | {item.pack_id for item in hits}
    covered = gold & keys
    recall = len(covered) / len(gold) if gold else None
    precision = len(covered) / len(keys) if keys else 0.0
    tokens = sum(item.bytes for item in hits) / 4
    unresolved: list[str] = []
    cost = None
    if cost_rate is not None:
        cost = tokens * cost_rate
    else:
        unresolved.append("cost_rate")
    return RetrievalComparison(
        strategy=name,  # type: ignore[arg-type]
        recall=round(recall, 4) if recall is not None else None,
        precision=round(precision, 4),
        latency_ms=round(latency_ms, 2),
        tokens=round(tokens, 1),
        cost=round(cost, 6) if cost is not None else None,
        unresolved=tuple(unresolved),
    )


def run_retrieval(
    corpus: Path, *, root: Path | None = None, cost_rate: float | None = None
) -> dict[str, Any]:
    cases = load_cases(corpus)
    policy = load_level_policy()
    results: list[dict[str, Any]] = []
    for case in cases:
        gold = set(case.get("gold") or ())
        strategies = tuple(case.get("strategies") or _STRATEGIES)
        comparisons = [
            _measure(
                name,
                case["query"],
                gold,
                HashEmbeddingAdapter() if case.get("semantic", True) else None,
                policy["hybrid"],
                policy["rerank"],
                root,
                cost_rate,
            )
            for name in strategies
        ]
        failures: list[str] = []
        expected = case.get("expect") or {}
        for comparison in comparisons:
            want = expected.get(comparison.strategy) or {}
            for key, value in want.items():
                actual = getattr(comparison, key)
                if key in {"recall", "precision"} and (actual or 0.0) < float(value):
                    failures.append(f"{comparison.strategy}.{key} {actual} < {value}")
        results.append(
            {
                "id": case["id"],
                "query": case["query"],
                "comparisons": [item.model_dump(mode="json") for item in comparisons],
                "passed": not failures,
                "failures": failures,
            }
        )
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/retrieval-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_retrieval"]
