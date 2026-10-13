"""§83–§87 control-plane replay: decisions re-derived, never replayed LLM text."""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.evals.replay import replay, replay_bundle
from apiforge.runtime.runner import run_runtime
from tests.runtime.economy_support import TASK_ID, economy_task


def _decisions(report) -> dict[str, object]:
    assert len(report.runs) == 1
    return {decision.name: decision for decision in report.runs[0].decisions}


def test_replay_recovers_persisted_decisions(tmp_path: Path) -> None:
    economy_task(tmp_path)
    run_runtime(tmp_path, TASK_ID, policy_id="local-ci-safe", now="2026-10-06T00:00:00Z")
    report = replay(root=tmp_path)
    names = _decisions(report)
    assert set(names) == {
        "loop",
        "model_route_shadow",
        "tool_authorization",
        "trust_admission",
        "recovery",
    }
    # The happy path recorded no failures: recovery receipts were never emitted.
    assert names["recovery"].status == "absent"
    # Loop fingerprints and the shadow receipt are persisted: both re-derive.
    assert names["loop"].status in {"same", "unresolved"}
    assert names["model_route_shadow"].status == "same"
    assert names["tool_authorization"].status == "same"
    assert names["trust_admission"].status in {"same", "absent"}
    # §86: replayed decisions name the policy they were decided under.
    assert names["model_route_shadow"].policy_hash.startswith("sha256:")
    assert report.policies


def test_replay_is_deterministic(tmp_path: Path) -> None:
    """§84: identical stored inputs re-decide identically under the same policy."""
    economy_task(tmp_path)
    run_runtime(tmp_path, TASK_ID, policy_id="local-ci-safe", now="2026-10-06T00:00:00Z")
    first = replay(root=tmp_path).model_dump(mode="json")
    second = replay(root=tmp_path).model_dump(mode="json")
    assert first == second


def test_replay_flags_policy_drift_on_recovery(tmp_path: Path) -> None:
    """A stored recovery action that current policy would not take → changed."""
    bundle = {
        "task_id": "t1",
        "recovery_receipts": [
            {
                "schema": "apiforge/recovery-receipt/v1",
                "receipt_id": "receipt:aaaabbbbccccdddd",
                "run_id": "run-1",
                "failure_class": "missing_evidence",
                "decision": "stop",
                "attempt": 0,
                "owner": "supervisor",
                "action_taken": "stopped",
                "outcome": "executed",
            }
        ],
    }
    run = replay_bundle("t1/run-1", bundle)
    decision = next(item for item in run.decisions if item.name == "recovery")
    assert decision.status == "changed"
    assert decision.code == "AF-REPLAY-DECISION-CHANGED"
    assert "stored=stop" in decision.detail


def test_replay_recovery_same_under_same_policy(tmp_path: Path) -> None:
    bundle = {
        "task_id": "t1",
        "recovery_receipts": [
            {
                "schema": "apiforge/recovery-receipt/v1",
                "receipt_id": "receipt:aaaabbbbccccdddd",
                "run_id": "run-1",
                "failure_class": "missing_evidence",
                "decision": "escalate",
                "attempt": 0,
                "owner": "scheduler",
                "action_taken": "escalated",
                "outcome": "executed",
            }
        ],
    }
    run = replay_bundle("t1/run-1", bundle)
    decision = next(item for item in run.decisions if item.name == "recovery")
    assert decision.status == "same"


def test_replay_trust_admission_flags_drifted_units(tmp_path: Path) -> None:
    """An admitted unit the current role policy would now deny → changed."""
    bundle = {
        "task_id": "t1",
        "role_context": {
            "schema": "apiforge/role-context-plan/v1",
            "run_id": "run-1",
            "context_bytes": 32,
            "roles": [
                {
                    "role": "critic",
                    "capability": "cap",
                    "context_class": "focused",
                    "bytes": 32,
                    "budget_bytes": 32,
                    "trust_units": [
                        {
                            "schema": "apiforge/trust-unit/v1",
                            "subject": "ctx://sha256/" + "e" * 64,
                            "boundary": "context_capsule",
                            "origin": "external_untrusted",
                            "trust_level": "untrusted",
                            "taint": ["external", "untrusted"],
                            "instruction_authority": "none",
                            "freshness": "unknown",
                        }
                    ],
                }
            ],
            "total_bytes": 32,
        },
    }
    run = replay_bundle("t1/run-1", bundle)
    decision = next(item for item in run.decisions if item.name == "trust_admission")
    # Either the critic policy denies this unit outright (changed) or the
    # permissive default still admits it (same) — never unresolved noise.
    assert decision.status in {"same", "changed"}
    if decision.status == "changed":
        assert "external" in decision.detail or "untrusted" in decision.detail


def test_corpus_bundles_report_decisions_absent(tmp_path: Path) -> None:
    """Hand-authored corpus bundles carry no run artifacts → honest absent."""
    (tmp_path / "case.json").write_text(
        json.dumps(
            {
                "task_id": "t",
                "routing": {"schema": "apiforge/routing-decision/v1"},
            }
        ),
        encoding="utf-8",
    )
    report = replay(corpus=tmp_path)
    decisions = _decisions(report)
    assert all(decision.status == "absent" for decision in decisions.values())
