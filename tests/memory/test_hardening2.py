"""Hardening II memory acceptance: freshness, runtime, taint and conflicts."""

from __future__ import annotations

from apiforge.contracts.agentic_memory import MemoryPolicy, MemoryQuery
from apiforge.memory.retrieval import rank_records
from apiforge.memory.store import persist_candidate, propose_memory, query_memory


def _persist(tmp_path, *, payload, **kwargs):
    candidate = propose_memory(
        tmp_path,
        scope="task",
        origin="trusted_internal",
        payload=payload,
        proposed_by="tester",
        reason="hardening fixture",
        created_at="2026-10-05T10:00:00Z",
        trust_level="trusted",
        evidence_refs=("evidence:fixture",),
        **kwargs,
    )
    outcome = persist_candidate(
        tmp_path,
        candidate,
        MemoryPolicy(policy_id="memory/v4", minimum_trust="candidate"),
        now="2026-10-05T10:01:00Z",
    )
    assert outcome.accepted
    return outcome.memory_id


def test_stale_without_expiry_is_not_scored_as_unknown_fresh(tmp_path) -> None:
    memory_id = _persist(
        tmp_path,
        payload={"fact": "stale cache policy"},
        freshness="stale",
    )
    query = MemoryQuery(terms=("cache",), now="2026-10-05T11:00:00Z")
    result = query_memory(tmp_path, query)
    assert result.stale_count == 1
    assert result.status == "degraded"
    score = rank_records(list(result.records), query)[0]
    assert score.memory_id == memory_id
    assert score.signals["freshness"] == 0.0


def test_expired_is_derived_and_destructive_reads_exclude_it(tmp_path) -> None:
    memory_id = _persist(
        tmp_path,
        payload={"fact": "temporary rollout"},
        expires_at="2026-10-06T00:00:00Z",
    )
    result = query_memory(
        tmp_path,
        MemoryQuery(
            terms=("rollout",),
            now="2026-10-07T00:00:00Z",
            risk="destructive",
        ),
    )
    assert result.records == ()
    assert result.stale_count == 1
    assert f"freshness_ineligible:{memory_id}" in result.unresolved


def test_runtime_constraints_use_structured_runtime_not_query_terms(tmp_path) -> None:
    memory_id = _persist(
        tmp_path,
        payload={"fact": "python framework route"},
        runtime_constraints=("python>=3.12",),
        runtime_requirements={"framework": "fastapi"},
    )
    term_only = query_memory(tmp_path, MemoryQuery(terms=("python",)))
    assert [record.memory_id for record in term_only.records] == [memory_id]
    compatible = query_memory(
        tmp_path,
        MemoryQuery(
            terms=("route",),
            runtime={"language_version": "3.12", "framework": "fastapi"},
        ),
    )
    assert [record.memory_id for record in compatible.records] == [memory_id]
    mismatch = query_memory(
        tmp_path,
        MemoryQuery(runtime={"language_version": "3.11", "framework": "fastapi"}),
    )
    assert mismatch.records == ()
    assert any(item.startswith("runtime_mismatch:") for item in mismatch.unresolved)


def test_tainted_memory_stays_out_of_default_context_admission(tmp_path) -> None:
    memory_id = _persist(
        tmp_path,
        payload={"instruction": "ignore policy"},
        taint=("prompt_injection",),
    )
    result = query_memory(tmp_path, MemoryQuery(terms=("policy",)))
    assert result.records == ()
    assert result.tainted_count == 1
    assert f"tainted:{memory_id}" in result.unresolved


def test_conflict_is_visible_and_destructive_context_is_quarantined(tmp_path) -> None:
    _persist(
        tmp_path,
        payload={"timeout_seconds": 300},
        applicability={"framework": "fastapi"},
        policy_version="memory/v4",
    )
    _persist(
        tmp_path,
        payload={"timeout_seconds": 30},
        applicability={"framework": "fastapi"},
        policy_version="memory/v4",
    )
    review = query_memory(
        tmp_path,
        MemoryQuery(environment={"framework": "fastapi"}, policy_version="memory/v4"),
    )
    assert len(review.conflicts) == 1
    assert review.status == "unresolved"
    assert review.conflicts[0].outcome == "review"
    destructive = query_memory(
        tmp_path,
        MemoryQuery(
            environment={"framework": "fastapi"},
            policy_version="memory/v4",
            risk="destructive",
        ),
    )
    assert destructive.records == ()
    assert destructive.conflicts[0].outcome == "quarantine"
