"""§14 gate pipeline: persist/quarantine/reject and the review boundary."""

from __future__ import annotations

from apiforge.contracts.agentic_memory import MemoryPolicy, MemoryQuery
from apiforge.memory.security import evaluate_gates
from apiforge.memory.store import (
    list_quarantine,
    persist_candidate,
    propose_memory,
    query_memory,
    review_quarantine,
)


def _candidate(tmp_path, *, scope="task", origin="trusted_internal", trust="trusted", **kw):
    return propose_memory(
        tmp_path,
        scope=scope,
        origin=origin,
        payload=kw.pop("payload", {"fact": "bounded"}),
        proposed_by="tester",
        reason="test",
        created_at="2026-10-05T10:00:00Z",
        trust_level=trust,
        **kw,
    )


def test_gates_preserve_hard_reject_codes(tmp_path) -> None:
    scope_denied = _candidate(tmp_path, scope="institutional", origin="verified_evidence")
    gate = evaluate_gates(scope_denied, MemoryPolicy(policy_id="p"), now="2026-10-05T10:01:00Z")
    assert gate.verdict == "reject"
    assert gate.code == "AF-MEMORY-SCOPE-DENIED"

    untrusted = _candidate(tmp_path, origin="external_untrusted", trust="trusted")
    gate = evaluate_gates(untrusted, MemoryPolicy(policy_id="p"), now="2026-10-05T10:01:00Z")
    assert gate.verdict == "reject"
    assert gate.code == "AF-MEMORY-UNTRUSTED"

    model = _candidate(tmp_path, origin="model_generated", trust="trusted")
    gate = evaluate_gates(model, MemoryPolicy(policy_id="p"), now="2026-10-05T10:01:00Z")
    assert gate.verdict == "reject"
    assert gate.code == "AF-MEMORY-MODEL-UNVERIFIED"


def test_trust_below_minimum_quarantines_instead_of_rejecting(tmp_path) -> None:
    candidate = _candidate(tmp_path, trust="candidate")
    outcome = persist_candidate(
        tmp_path, candidate, MemoryPolicy(policy_id="p"), now="2026-10-05T10:01:00Z"
    )
    assert outcome.action == "quarantined"
    assert outcome.accepted is False
    assert outcome.code == "AF-MEMORY-TRUST-QUARANTINED"

    rows = list_quarantine(tmp_path)
    assert len(rows) == 1
    assert rows[0].state == "quarantined"
    assert rows[0].candidate_id == candidate.candidate_id

    # quarantined candidates never reach the retrieval surface
    result = query_memory(tmp_path, MemoryQuery(now="2026-10-05T10:02:00Z"))
    assert not result.records


def test_expired_candidate_is_rejected_at_persist(tmp_path) -> None:
    candidate = _candidate(tmp_path, expires_at="2026-10-05T09:00:00Z")
    outcome = persist_candidate(
        tmp_path, candidate, MemoryPolicy(policy_id="p"), now="2026-10-05T10:01:00Z"
    )
    assert outcome.action == "rejected"
    assert outcome.code == "AF-MEMORY-EXPIRED"


def test_quarantine_review_persists_only_when_gates_pass(tmp_path) -> None:
    candidate = _candidate(tmp_path, trust="candidate")
    persist_candidate(tmp_path, candidate, MemoryPolicy(policy_id="p"), now="2026-10-05T10:01:00Z")
    # same policy → still below minimum trust → stays quarantined
    outcome = review_quarantine(
        tmp_path,
        candidate.candidate_id,
        MemoryPolicy(policy_id="p"),
        verdict="persist",
        resolved_by="reviewer",
        now="2026-10-05T10:02:00Z",
    )
    assert outcome.action == "quarantined"
    assert not outcome.accepted

    # revised policy (a human lowered the floor explicitly) releases it
    outcome = review_quarantine(
        tmp_path,
        candidate.candidate_id,
        MemoryPolicy(policy_id="p-relaxed", minimum_trust="candidate"),
        verdict="persist",
        resolved_by="reviewer",
        now="2026-10-05T10:03:00Z",
    )
    assert outcome.action == "accepted"
    assert outcome.accepted

    rows = list_quarantine(tmp_path)
    assert any(row.state == "released" and row.verdict == "persisted" for row in rows)


def test_quarantine_review_reject_is_append_only(tmp_path) -> None:
    candidate = _candidate(tmp_path, trust="candidate")
    persist_candidate(tmp_path, candidate, MemoryPolicy(policy_id="p"), now="2026-10-05T10:01:00Z")
    outcome = review_quarantine(
        tmp_path,
        candidate.candidate_id,
        MemoryPolicy(policy_id="p"),
        verdict="reject",
        resolved_by="reviewer",
        now="2026-10-05T10:02:00Z",
    )
    assert outcome.code == "AF-MEMORY-QUARANTINE-REJECTED"
    # a second review of the same candidate finds nothing pending
    second = review_quarantine(
        tmp_path,
        candidate.candidate_id,
        MemoryPolicy(policy_id="p"),
        verdict="reject",
        resolved_by="reviewer",
        now="2026-10-05T10:03:00Z",
    )
    assert second.code == "AF-MEMORY-QUARANTINE-NOT-FOUND"
