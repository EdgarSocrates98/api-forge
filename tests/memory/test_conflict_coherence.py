"""Final-convergence memory admission: conflict outcome must match the
returned record set. ``prefer_*`` is advisory (never destructive authority),
``quarantine`` excludes both rows, ``review`` keeps both but non-decisional.
"""

from __future__ import annotations

from apiforge.contracts.agentic_memory import MemoryPolicy, MemoryQuery
from apiforge.memory.store import persist_candidate, propose_memory, query_memory

NOW = "2026-10-06T10:01:00Z"


def _persist(tmp_path, *, payload, trust="trusted", origin="trusted_internal", **kwargs):
    candidate = propose_memory(
        tmp_path,
        scope="task",
        origin=origin,
        payload=payload,
        proposed_by="tester",
        reason="final-convergence fixture",
        created_at="2026-10-06T10:00:00Z",
        trust_level=trust,
        evidence_refs=kwargs.pop("evidence_refs", ("evidence:fixture",)),
        **kwargs,
    )
    outcome = persist_candidate(
        tmp_path,
        candidate,
        MemoryPolicy(policy_id="memory/v4", minimum_trust="candidate"),
        now=NOW,
    )
    assert outcome.accepted
    return outcome.memory_id


def _strong_pair(tmp_path):
    """Two applicable, fresh, contradictory rows where A dominates B."""
    strong = _persist(
        tmp_path,
        payload={"timeout_seconds": 300},
        trust="verified",
        origin="system",
        evidence_refs=("evidence:a1", "evidence:a2", "evidence:a3"),
        policy_version="memory/v4",
    )
    weak = _persist(
        tmp_path,
        payload={"timeout_seconds": 30},
        trust="observed",
        origin="tool_result",
        evidence_refs=(),
        policy_version="memory/v5",
    )
    return strong, weak


def _equal_pair(tmp_path):
    left = _persist(tmp_path, payload={"timeout_seconds": 300})
    right = _persist(tmp_path, payload={"timeout_seconds": 30})
    return left, right


def test_read_only_strong_preference_identifies_preferred_and_loser(tmp_path) -> None:
    strong, weak = _strong_pair(tmp_path)
    result = query_memory(tmp_path, MemoryQuery(now=NOW))
    assert len(result.conflicts) == 1
    conflict = result.conflicts[0]
    # a/b label follows the sorted memory_id pair, not the score — the
    # preferred side must be read from preferred_memory_id.
    assert conflict.outcome in {"prefer_a", "prefer_b"}
    assert conflict.admission_effect == "admit_preferred"
    assert conflict.preferred_memory_id == strong
    assert conflict.conflicting_memory_id == weak
    served = {record.memory_id for record in result.records}
    assert served == {strong}
    # audit trail keeps the losing side: id, paths and signals survive
    assert weak in {conflict.memory_a_id, conflict.memory_b_id}
    assert conflict.conflicting_paths
    assert conflict.signals["a_trust"] != conflict.signals["b_trust"]
    assert result.status == "unresolved"


def test_sensitive_strong_preference_is_advisory_not_quarantine(tmp_path) -> None:
    strong, weak = _strong_pair(tmp_path)
    result = query_memory(tmp_path, MemoryQuery(risk="sensitive", now=NOW))
    conflict = result.conflicts[0]
    assert conflict.outcome in {"prefer_a", "prefer_b"}
    assert conflict.preferred_memory_id == strong
    assert conflict.conflicting_memory_id == weak
    assert {record.memory_id for record in result.records} == {strong}


def test_destructive_strong_preference_quarantines_both(tmp_path) -> None:
    strong, weak = _strong_pair(tmp_path)
    result = query_memory(tmp_path, MemoryQuery(risk="destructive", now=NOW))
    conflict = result.conflicts[0]
    assert conflict.outcome == "quarantine"
    assert conflict.admission_effect == "exclude_both"
    assert conflict.preferred_memory_id is None
    assert conflict.conflicting_memory_id is None
    assert result.records == ()
    assert result.status == "unresolved"
    # both rows stay in the conflict audit trail
    assert {conflict.memory_a_id, conflict.memory_b_id} == {strong, weak}
    assert "destructive action requires conflict quarantine" in conflict.unresolved


def test_destructive_equal_scores_quarantine(tmp_path) -> None:
    left, right = _equal_pair(tmp_path)
    result = query_memory(tmp_path, MemoryQuery(risk="destructive", now=NOW))
    conflict = result.conflicts[0]
    assert conflict.outcome == "quarantine"
    assert result.records == ()
    assert {conflict.memory_a_id, conflict.memory_b_id} == {left, right}


def test_review_keeps_both_visible_but_non_decisional(tmp_path) -> None:
    left, right = _equal_pair(tmp_path)
    result = query_memory(tmp_path, MemoryQuery(now=NOW))
    conflict = result.conflicts[0]
    assert conflict.outcome == "review"
    assert conflict.admission_effect == "review_only"
    assert conflict.preferred_memory_id is None
    assert {record.memory_id for record in result.records} == {left, right}
    assert result.status == "unresolved"
    assert "conflicting applicable memory requires review" in conflict.unresolved


def test_conflict_outcome_coherence_with_result_set(tmp_path) -> None:
    """For every risk class the served records must match admission_effect."""
    strong, weak = _strong_pair(tmp_path)
    for risk, expected_outcome, expected_records in (
        ("read_only", "prefer", {strong}),
        ("sensitive", "prefer", {strong}),
        ("destructive", "quarantine", set()),
    ):
        result = query_memory(tmp_path, MemoryQuery(risk=risk, now=NOW))
        conflict = result.conflicts[0]
        served = {record.memory_id for record in result.records}
        if expected_outcome == "prefer":
            assert conflict.outcome in {"prefer_a", "prefer_b"}
            assert conflict.preferred_memory_id == strong
            assert conflict.conflicting_memory_id == weak
        else:
            assert conflict.outcome == expected_outcome
        assert served == expected_records
        assert result.status == "unresolved"
        assert any(
            f"conflict:{conflict.conflict_id}:{conflict.outcome}" == item
            for item in result.unresolved
        )
        # contradictory evidence remains reachable through the conflict row
        assert strong in {conflict.memory_a_id, conflict.memory_b_id}
        assert weak in {conflict.memory_a_id, conflict.memory_b_id}


def test_prefer_never_authorizes_destructive(tmp_path) -> None:
    """Even a dominant score must not surface prefer_* under destructive risk."""
    strong, _weak = _strong_pair(tmp_path)
    result = query_memory(tmp_path, MemoryQuery(risk="destructive", now=NOW))
    assert all(conflict.outcome not in {"prefer_a", "prefer_b"} for conflict in result.conflicts)
    assert all(conflict.admission_effect == "exclude_both" for conflict in result.conflicts)
    assert strong not in {record.memory_id for record in result.records}
