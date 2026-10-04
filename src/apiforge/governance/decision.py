"""Fail-closed decision admission for risky agentic actions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from apiforge.contracts.agentic import AgenticPolicy, ApprovalGate
from apiforge.contracts.agentic_governance import DecisionGateResult, DecisionRequest

APPROVAL_REQUIRED = "AF-GOV-APPROVAL-REQUIRED"
APPROVAL_PENDING = "AF-GOV-APPROVAL-PENDING"
APPROVAL_REJECTED = "AF-GOV-APPROVAL-REJECTED"
POLICY_DENIED = "AF-GOV-POLICY-DENIED"
EVIDENCE_REQUIRED = "AF-GOV-EVIDENCE-REQUIRED"
STORE_CORRUPT = "AF-GOV-STORE-CORRUPT"

_DIR = Path(".apiforge") / "governance"
_FILE = "decision-gates.jsonl"
_APPROVAL_RISKS = {"sensitive", "external_mutation", "destructive", "irreversible"}
_MUTATION_RISKS = {"external_mutation", "destructive", "irreversible"}


def evaluate_decision(
    request: DecisionRequest,
    *,
    policy: AgenticPolicy | None = None,
    approval: ApprovalGate | None = None,
) -> DecisionGateResult:
    """Evaluate a proposal; never infer approval from the proposal text."""
    if request.risk in _MUTATION_RISKS and policy is not None and not policy.allow_external_mutation:
        return _result(
            request, "block", POLICY_DENIED, "policy.allow_external_mutation",
            "use a policy that explicitly allows the risk and retains a human gate",
            "external mutation is disabled by policy",
        )
    if request.risk != "read_only" and not request.evidence_refs:
        return _result(
            request, "review", EVIDENCE_REQUIRED, "evidence_refs",
            "attach independently verified evidence before approval", "non-read-only action lacks evidence",
        )
    if request.risk in _APPROVAL_RISKS:
        if approval is None:
            return _result(
                request, "review", APPROVAL_REQUIRED, "approval_id",
                "create a human ApprovalGate; model text cannot approve the action",
                "risk requires an explicit approval artifact",
            )
        if approval.status == "pending":
            return _result(
                request, "review", APPROVAL_PENDING, "approval.status",
                "a human must decide the ApprovalGate", "approval is still pending",
                approval.gate_id,
            )
        if approval.status == "rejected":
            return _result(
                request, "block", APPROVAL_REJECTED, "approval.status",
                "create a new reviewed request if the action is still necessary",
                "human approval was rejected", approval.gate_id,
            )
        return _result(request, "allow", None, None, None, "approved human gate", approval.gate_id)
    return _result(request, "allow", None, None, None, "read-only or local reversible action")


def _result(
    request: DecisionRequest,
    outcome: str,
    code: str | None,
    field: str | None,
    unlock: str | None,
    reason: str,
    approval_id: str | None = None,
) -> DecisionGateResult:
    return DecisionGateResult(
        request_id=request.request_id, task_id=request.task_id, run_id=request.run_id,
        action=request.action, risk=request.risk, outcome=cast(Any, outcome),
        approval_id=approval_id, code=code, field=field, unlock=unlock,
        reason=reason, evidence_refs=request.evidence_refs,
    )


def _directory(root: Path) -> Path:
    resolved = Path(root).resolve()
    if resolved.name == ".apiforge":
        resolved = resolved.parent
    return resolved / _DIR


def persist_decision(root: Path, result: DecisionGateResult) -> dict[str, object]:
    """Append a decision result idempotently for audit and later review."""
    directory = _directory(root)
    path = directory / _FILE
    existing: list[DecisionGateResult] = []
    if path.is_file():
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                existing.append(DecisionGateResult.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"{STORE_CORRUPT}: {path}:{line_no}: {exc}") from exc
    for item in existing:
        if item.request_id == result.request_id:
            if item.model_dump(mode="json") != result.model_dump(mode="json"):
                raise ValueError("AF-GOV-DECISION-CONFLICT: request_id maps to a different result")
            return {"status": "deduplicated", "result": item.model_dump(mode="json")}
    directory.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(result.model_dump_json())
        handle.write("\n")
    return {"status": "accepted", "result": result.model_dump(mode="json")}


__all__ = ["evaluate_decision", "persist_decision"]
