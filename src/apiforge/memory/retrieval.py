"""Deterministic memory ranking (step11 §15).

Progressive signals: exact id → lexical coverage → environment and runtime
compatibility → freshness → trust → outcome → evidence depth. Semantic
similarity is an optional caller-supplied bonus, never a dependency.
"""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.agentic_memory import MemoryQuery, MemoryRecord
from apiforge.contracts.trust import MemoryRankedResult, MemoryScore
from apiforge.memory.matching import effective_freshness, runtime_match

_TRUST_ORDER = {
    "unknown": 0,
    "candidate": 1,
    "untrusted": 1,
    "observed": 2,
    "trusted": 3,
    "verified": 4,
}

#: Deterministic signal weights; they sum to 1.0 without the optional bonus.
_WEIGHTS = {
    "exact": 0.05,
    "lexical": 0.25,
    "env_compat": 0.15,
    "runtime_compat": 0.05,
    "freshness": 0.15,
    "trust": 0.20,
    "outcome": 0.10,
    "evidence": 0.05,
}
_SEMANTIC_BONUS = 0.05


def _term_coverage(searchable: str, terms: tuple[str, ...]) -> float:
    if not terms:
        return 1.0
    return sum(term.lower() in searchable for term in terms) / len(terms)


def score_record(
    record: MemoryRecord, query: MemoryQuery, *, semantic_score: float | None = None
) -> MemoryScore:
    """Decompose a record's retrieval score into named signals."""
    searchable = json.dumps(record.payload, sort_keys=True, ensure_ascii=False).lower()
    terms = [term.lower() for term in query.terms]
    exact = 1.0 if record.memory_id in query.terms else 0.0
    lexical = _term_coverage(searchable, query.terms) if terms else 0.5
    if query.environment:
        env_compat = sum(
            record.applicability.get(key) == value for key, value in query.environment.items()
        ) / len(query.environment)
    elif not query.environment_fingerprint or record.environment_fingerprint is None:
        env_compat = 0.5
    else:
        env_compat = float(record.environment_fingerprint == query.environment_fingerprint)
    _, runtime_compat, _ = runtime_match(record, query.runtime)
    freshness_state = effective_freshness(record, query.now)
    freshness = {
        "fresh": 1.0,
        "stale": 0.0,
        "expired": 0.0,
        "unknown": 0.5,
        "unresolved": 0.25,
    }.get(freshness_state, 0.25)
    trust = _TRUST_ORDER[record.trust_level] / 4.0
    outcome = 1.0 if record.outcome in {"persisted", "reinforced"} else 0.5
    evidence = min(1.0, len(record.evidence_refs) / 2.0)
    signals = {
        "exact": exact,
        "lexical": lexical,
        "env_compat": env_compat,
        "runtime_compat": runtime_compat,
        "freshness": freshness,
        "trust": trust,
        "outcome": outcome,
        "evidence": evidence,
    }
    score = sum(_WEIGHTS[name] * value for name, value in signals.items())
    if semantic_score is not None:
        signals["semantic"] = semantic_score
        score += _SEMANTIC_BONUS * semantic_score
    return MemoryScore(memory_id=record.memory_id, score=round(score, 6), signals=signals)


def rank_records(
    records: list[MemoryRecord],
    query: MemoryQuery,
    *,
    semantic_scores: dict[str, float] | None = None,
) -> tuple[MemoryScore, ...]:
    """Rank records by descending score; ties break on memory_id."""
    scored = [
        score_record(
            record,
            query,
            semantic_score=(semantic_scores or {}).get(record.memory_id),
        )
        for record in records
    ]
    scored.sort(key=lambda item: (-item.score, item.memory_id))
    return tuple(scored)


def query_memory_scored(
    root: Path, query: MemoryQuery, *, semantic_scores: dict[str, float] | None = None
) -> MemoryRankedResult:
    """Governed retrieval plus per-record score decomposition."""
    from apiforge.memory.store import query_memory

    result = query_memory(root, query)
    ranked = rank_records(list(result.records), query, semantic_scores=semantic_scores)
    return MemoryRankedResult(
        query=query,
        ranked=ranked[: query.max_results],
        conflicts=result.conflicts,
        unresolved=result.unresolved,
    )


__all__ = ["query_memory_scored", "rank_records", "score_record"]
