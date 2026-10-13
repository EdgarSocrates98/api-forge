"""§16 invalidation triggers: advisory plans, never mutations."""

from __future__ import annotations

from apiforge.contracts.agentic_memory import MemoryPolicy, MemoryQuery
from apiforge.memory.invalidation import suggest_invalidations
from apiforge.memory.store import persist_candidate, propose_memory, query_memory


def _persist(tmp_path, *, env=None, provenance=(), evidence=(), applicability=None, tag=""):
    candidate = propose_memory(
        tmp_path,
        scope="task",
        origin="verified_evidence",
        payload={"fact": f"probe{tag}"},
        proposed_by="tester",
        reason="fixture",
        created_at="2026-10-05T10:00:00Z",
        trust_level="verified",
        environment_fingerprint=env,
        provenance=provenance,
        evidence_refs=evidence,
        applicability=applicability or {},
    )
    outcome = persist_candidate(
        tmp_path,
        candidate,
        MemoryPolicy(policy_id="p", minimum_trust="candidate"),
        now="2026-10-05T10:01:00Z",
    )
    assert outcome.accepted
    return outcome.memory_id or ""


def test_runtime_change_flags_mismatched_environments(tmp_path) -> None:
    old = _persist(tmp_path, env="repo:py310", tag="-old")
    current = _persist(tmp_path, env="repo:py312", tag="-current")
    _persist(tmp_path, tag="-envless")  # env-less records are untouched
    plan = suggest_invalidations(tmp_path, "runtime_change", environment_fingerprint="repo:py312")
    assert old in plan.memory_ids
    assert current not in plan.memory_ids
    assert plan.unresolved == ()


def test_missing_fingerprint_is_unresolved_not_silent(tmp_path) -> None:
    _persist(tmp_path, env="repo:py310")
    plan = suggest_invalidations(tmp_path, "runtime_change")
    assert plan.memory_ids == ()
    assert plan.unresolved


def test_source_change_flags_touched_provenance(tmp_path) -> None:
    touched = _persist(tmp_path, provenance=("spec:openapi.yaml",))
    _persist(tmp_path, provenance=("spec:other.yaml",))
    plan = suggest_invalidations(tmp_path, "source_change", changed=("openapi.yaml",))
    assert plan.memory_ids == (touched,)


def test_contract_change_searches_applicability_and_evidence(tmp_path) -> None:
    touched = _persist(tmp_path, evidence=("evidence:contract-diff-7",))
    plan = suggest_invalidations(tmp_path, "contract_change", changed=("contract-diff-7",))
    assert plan.memory_ids == (touched,)


def test_outcome_invalid_requires_explicit_ids(tmp_path) -> None:
    memory_id = _persist(tmp_path)
    plan = suggest_invalidations(tmp_path, "outcome_invalid", memory_ids=(memory_id,))
    assert plan.memory_ids == (memory_id,)
    empty = suggest_invalidations(tmp_path, "contradicting_evidence")
    assert empty.memory_ids == ()
    assert empty.unresolved


def test_plans_skip_already_invalidated_records(tmp_path) -> None:
    from apiforge.memory.store import invalidate_memory

    memory_id = _persist(tmp_path, env="repo:py310")
    invalidate_memory(
        tmp_path,
        memory_id,
        reason="manually superseded",
        invalidated_by="reviewer",
        created_at="2026-10-05T10:02:00Z",
    )
    plan = suggest_invalidations(tmp_path, "runtime_change", environment_fingerprint="repo:py312")
    assert memory_id not in plan.memory_ids


def test_plan_does_not_mutate_the_store(tmp_path) -> None:
    _persist(tmp_path, env="repo:py310")
    suggest_invalidations(tmp_path, "runtime_change", environment_fingerprint="repo:py312")
    result = query_memory(tmp_path, MemoryQuery(now="2026-10-05T11:00:00Z"))
    assert len(result.records) == 1
    assert result.invalidated_count == 0
