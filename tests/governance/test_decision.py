from __future__ import annotations

from pathlib import Path

from apiforge.contracts.agentic import AgenticPolicy, ApprovalGate
from apiforge.contracts.agentic_governance import DecisionRequest
from apiforge.governance.decision import evaluate_decision, persist_decision
from apiforge.mcp import tools


def _request(risk: str = "read_only") -> DecisionRequest:
    return DecisionRequest(
        request_id=f"request-{risk}", task_id="task-1", run_id="run-1",
        action="inspect", risk=risk, proposed_by="agent:test",
        evidence_refs=("fact:verified",) if risk != "read_only" else (),
        requested_at="2026-10-04T12:00:00Z",
    )


def _approval(status: str) -> ApprovalGate:
    return ApprovalGate(
        gate_id="gate-1", run_id="run-1", reason="external mutation",
        requested_action="inspect", status=status, requested_by="agent:test",
    )


def test_default_policy_blocks_external_mutation() -> None:
    result = evaluate_decision(_request("external_mutation"), policy=AgenticPolicy(policy_id="local"))
    assert result.outcome == "block"
    assert result.code == "AF-GOV-POLICY-DENIED"


def test_approval_lifecycle_is_explicit() -> None:
    policy = AgenticPolicy(policy_id="reviewed", allow_external_mutation=True)
    pending = evaluate_decision(_request("external_mutation"), policy=policy, approval=_approval("pending"))
    assert pending.outcome == "review"
    assert pending.code == "AF-GOV-APPROVAL-PENDING"
    approved = evaluate_decision(_request("external_mutation"), policy=policy, approval=_approval("approved"))
    assert approved.outcome == "allow"
    rejected = evaluate_decision(_request("external_mutation"), policy=policy, approval=_approval("rejected"))
    assert rejected.outcome == "block"


def test_gate_record_is_idempotent_and_mcp_uses_same_evaluator(tmp_path: Path) -> None:
    result = evaluate_decision(_request(), policy=AgenticPolicy(policy_id="local"))
    assert persist_decision(tmp_path, result)["status"] == "accepted"
    assert persist_decision(tmp_path, result)["status"] == "deduplicated"
    projected = tools.decision_check(
        _request().model_dump(mode="json"), root=str(tmp_path), policy={"policy_id": "local"}
    )
    assert projected["result"]["outcome"] == "allow"
