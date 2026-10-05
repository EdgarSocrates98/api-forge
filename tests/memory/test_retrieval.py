"""§15 deterministic ranking: signals, ordering, optional semantics."""

from __future__ import annotations

from apiforge.contracts.agentic_memory import MemoryPolicy, MemoryQuery
from apiforge.memory.retrieval import query_memory_scored, rank_records
from apiforge.memory.store import persist_candidate, propose_memory, query_memory


def _persist(
    tmp_path,
    *,
    payload,
    trust="trusted",
    scope="task",
    env=None,
    constraints=(),
    applicability=None,
):
    candidate = propose_memory(
        tmp_path,
        scope=scope,
        origin="trusted_internal",
        payload=payload,
        proposed_by="tester",
        reason="fixture",
        created_at="2026-10-05T10:00:00Z",
        trust_level=trust,
        environment_fingerprint=env,
        runtime_constraints=constraints,
        applicability=applicability,
    )
    outcome = persist_candidate(
        tmp_path,
        candidate,
        MemoryPolicy(policy_id="p", minimum_trust="candidate"),
        now="2026-10-05T10:01:00Z",
    )
    assert outcome.accepted
    return outcome.memory_id


def test_ranking_orders_by_deterministic_signals(tmp_path) -> None:
    strong = _persist(
        tmp_path,
        payload={"fact": "cache key ttl is 300 seconds", "detail": "verified"},
        trust="verified",
        env="repo:a",
        constraints=("python>=3.12",),
    )
    weak = _persist(
        tmp_path,
        payload={"note": "unrelated housekeeping"},
        trust="candidate",
        env="repo:b",
    )
    query = MemoryQuery(
        terms=("cache", "ttl"), environment_fingerprint="repo:a", now="2026-10-05T11:00:00Z"
    )
    result = query_memory_scored(tmp_path, query)
    # env mismatch keeps `weak` out entirely; `strong` ranks first by score
    assert result.ranked
    assert result.ranked[0].memory_id == strong
    assert weak not in {item.memory_id for item in result.ranked}
    top = result.ranked[0]
    assert top.signals["lexical"] == 1.0
    assert top.signals["env_compat"] == 1.0
    assert top.signals["trust"] == 1.0


def test_query_memory_returns_ranked_order(tmp_path) -> None:
    high = _persist(tmp_path, payload={"fact": "alpha evidence bound"}, trust="trusted")
    low = _persist(tmp_path, payload={"fact": "alpha weak guess"}, trust="candidate")
    result = query_memory(tmp_path, MemoryQuery(terms=("alpha",), now="2026-10-05T11:00:00Z"))
    assert [record.memory_id for record in result.records] == [high, low]


def test_semantic_bonus_is_optional_and_additive(tmp_path) -> None:
    memory_id = _persist(tmp_path, payload={"fact": "semantic probe"}, trust="candidate")
    query = MemoryQuery(terms=("semantic",), now="2026-10-05T11:00:00Z")
    records = list(query_memory(tmp_path, query).records)
    plain = rank_records(records, query)
    boosted = rank_records(records, query, semantic_scores={memory_id or "": 1.0})
    assert plain[0].score < boosted[0].score
    assert "semantic" not in plain[0].signals
    assert boosted[0].signals["semantic"] == 1.0


def test_term_coverage_is_configurable_between_or_and_all(tmp_path) -> None:
    memory_id = _persist(tmp_path, payload={"fact": "alpha evidence"}, trust="candidate")
    default = query_memory(tmp_path, MemoryQuery(terms=("alpha", "missing")))
    assert [item.memory_id for item in default.records] == [memory_id]
    strict = query_memory(tmp_path, MemoryQuery(terms=("alpha", "missing"), min_term_coverage=1.0))
    assert strict.records == ()


def test_structured_environment_compatibility_is_a_filter(tmp_path) -> None:
    compatible = _persist(
        tmp_path,
        payload={"fact": "framework route"},
        applicability={"language": "python", "framework": "fastapi"},
    )
    _persist(
        tmp_path,
        payload={"fact": "framework route"},
        applicability={"language": "go", "framework": "chi"},
    )
    result = query_memory(
        tmp_path,
        MemoryQuery(
            terms=("route",),
            environment={"language": "python", "framework": "fastapi"},
        ),
    )
    assert [item.memory_id for item in result.records] == [compatible]
