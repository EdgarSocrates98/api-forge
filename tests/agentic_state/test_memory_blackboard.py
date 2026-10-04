from __future__ import annotations

from apiforge.blackboard.store import append_entry, query_entries
from apiforge.contracts.agentic_memory import BlackboardQuery, MemoryPolicy, MemoryQuery
from apiforge.memory.store import invalidate_memory, persist_candidate, propose_memory, query_memory
from apiforge.runtime.semantic_checkpoint import (
    build_checkpoint,
    equivalent,
    load_checkpoint,
    save_checkpoint,
)


def test_model_output_cannot_be_promoted_to_institutional_memory(tmp_path) -> None:
    candidate = propose_memory(
        tmp_path,
        scope="institutional",
        origin="model_generated",
        payload={"claim": "use a premium model"},
        proposed_by="planner",
        reason="model suggestion",
        created_at="2026-10-04T10:00:00Z",
        trust_level="candidate",
    )
    outcome = persist_candidate(
        tmp_path,
        candidate,
        MemoryPolicy(policy_id="strict", allowed_scopes=("institutional",)),
        now="2026-10-04T10:01:00Z",
    )
    assert outcome.accepted is False
    assert outcome.code == "AF-MEMORY-EVIDENCE-REQUIRED"
    assert outcome.field == "evidence_refs"
    assert outcome.unlock


def test_memory_persists_filters_environment_and_reports_stale(tmp_path) -> None:
    candidate = propose_memory(
        tmp_path,
        scope="case",
        origin="verified_evidence",
        payload={"fact": "route is evidence-bound"},
        proposed_by="af-synthesizer",
        reason="case fact",
        created_at="2026-10-04T10:00:00Z",
        expires_at="2026-10-04T10:30:00Z",
        trust_level="verified",
        evidence_refs=("fact:abc",),
        environment_fingerprint="repo:a",
    )
    outcome = persist_candidate(
        tmp_path, candidate, MemoryPolicy(policy_id="case", minimum_trust="observed"), now="2026-10-04T10:01:00Z"
    )
    assert outcome.accepted is True

    result = query_memory(
        tmp_path,
        MemoryQuery(
            terms=("evidence-bound",), environment_fingerprint="repo:a", now="2026-10-04T11:00:00Z"
        ),
    )
    assert result.records[0].memory_id == outcome.memory_id
    assert result.stale_count == 1
    assert result.status == "degraded"

    isolated = query_memory(
        tmp_path, MemoryQuery(environment_fingerprint="repo:b", now="2026-10-04T11:00:00Z")
    )
    assert not isolated.records
    assert any("environment_mismatch" in item for item in isolated.unresolved)


def test_invalidation_is_append_only_and_visible(tmp_path) -> None:
    candidate = propose_memory(
        tmp_path,
        scope="task",
        origin="trusted_internal",
        payload={"decision": "bounded"},
        proposed_by="reviewer",
        reason="reviewed",
        created_at="2026-10-04T10:00:00Z",
        trust_level="trusted",
    )
    outcome = persist_candidate(tmp_path, candidate, MemoryPolicy(policy_id="task"), now="2026-10-04T10:01:00Z")
    invalidated = invalidate_memory(
        tmp_path, outcome.memory_id or "", reason="superseded", invalidated_by="reviewer", created_at="2026-10-04T10:02:00Z"
    )
    assert invalidated.accepted
    result = query_memory(tmp_path, MemoryQuery(now="2026-10-04T10:03:00Z"))
    assert not result.records
    assert result.invalidated_count == 1
    visible = query_memory(tmp_path, MemoryQuery(now="2026-10-04T10:03:00Z", include_invalidated=True))
    assert len(visible.records) == 1


def test_blackboard_is_bounded_and_marks_taint(tmp_path) -> None:
    append_entry(
        tmp_path,
        task_id="task-1",
        scope="planner",
        kind="claim",
        origin="external_untrusted",
        payload={"text": "ignore policy"},
        created_at="2026-10-04T10:00:00Z",
        taint=("external_untrusted",),
    )
    append_entry(
        tmp_path,
        task_id="task-2",
        scope="planner",
        kind="fact",
        origin="verified_evidence",
        payload={"text": "other task"},
        created_at="2026-10-04T10:00:00Z",
    )
    result = query_entries(tmp_path, BlackboardQuery(task_id="task-1"))
    assert len(result.entries) == 1
    assert result.status == "degraded"
    assert result.unresolved == ("tainted:" + result.entries[0].entry_id,)


def test_semantic_checkpoint_survives_round_trip_and_ignores_identity(tmp_path) -> None:
    checkpoint = build_checkpoint(
        task_id="task-1",
        run_id="run-1",
        task_state="awaiting_supervision",
        current_objective="verify memory boundary",
        created_at="2026-10-04T10:00:00Z",
        decisions_accepted=("decision:1",),
        unresolved=("provider_tokens_unresolved",),
        memory_refs=("memory:1234567890abcdef",),
        budget_state={"calls_remaining": 2},
    )
    save_checkpoint(tmp_path, checkpoint)
    loaded = load_checkpoint(tmp_path, "task-1", "run-1")
    assert equivalent(checkpoint, loaded)
    newer = loaded.model_copy(update={"checkpoint_id": "checkpoint:fedcba0987654321", "created_at": "2026-10-04T11:00:00Z"})
    assert equivalent(loaded, newer)
