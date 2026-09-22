"""Render an OutcomeBrief from a task record — DONE is refused, not advised.

Status mapping is data, not mood:

- ``accepted`` + proof -> DONE (the contract validator refuses otherwise)
- ``awaiting_supervision`` -> DECIDE (a human must accept or reject)
- ``blocked`` -> BLOCKED (the gaps are the named blockers)
- ``parked`` -> DECIDE (a human must unpark or expire)
- ``rejected``/``expired`` -> FAILED
- ``running`` -> REVIEW (in flight)
- ``draft``/``reviewed``/``sealed``/``ready`` -> DECIDE (lifecycle pending)
"""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import BriefStatus, OutcomeBrief, TaskState
from apiforge.taskspec import store
from apiforge.verification.service import load_verification


def _acceptance_proof(root: Path, task_id: str) -> tuple[str, ...]:
    history = store.history(root, task_id)
    for entry in reversed(history):
        if entry.get("event") == "->accepted":
            evidence = entry.get("evidence")
            if isinstance(evidence, list) and evidence:
                return tuple(str(e) for e in evidence)
            return (f"history: accepted by {entry.get('by')}",)
    return ()


def brief_for_task(root: Path, task_id: str) -> OutcomeBrief:
    spec = store.load(root, task_id)
    state = spec.state
    if state is TaskState.ACCEPTED:
        if spec.strategy.value == "verified-api-slice":
            try:
                verification = load_verification(root, task_id)
            except ContractError:
                return OutcomeBrief(
                    status=BriefStatus.REVIEW,
                    outcome=spec.outcome,
                    human_action="run independent verification before accepting",
                    gaps=("verification record is missing",),
                    subject=task_id,
                )
            if verification.verdict != "pass":
                return OutcomeBrief(
                    status=BriefStatus.REVIEW,
                    outcome=spec.outcome,
                    human_action="resolve verification gaps before accepting",
                    gaps=verification.gaps or (f"verification: {verification.verdict}",),
                    proof=verification.evidence,
                    subject=task_id,
                )
        return OutcomeBrief(
            status=BriefStatus.DONE,
            outcome=spec.outcome,
            proof=_acceptance_proof(root, task_id),
            subject=task_id,
        )
    if state is TaskState.AWAITING_SUPERVISION:
        return OutcomeBrief(
            status=BriefStatus.DECIDE,
            outcome=spec.outcome,
            human_action="accept or reject the run (`task accept|reject`)",
            proof=(f"run record under {store.task_dir(root, task_id) / 'runs'}",),
            subject=task_id,
        )
    if state is TaskState.BLOCKED:
        blockers = tuple(
            str(e.get("reason", "blocked"))
            for e in store.history(root, task_id)
            if e.get("event") == "->blocked"
        ) or ("blocked — see history",)
        return OutcomeBrief(
            status=BriefStatus.BLOCKED,
            outcome=spec.outcome,
            gaps=blockers,
            subject=task_id,
        )
    if state is TaskState.PARKED:
        return OutcomeBrief(
            status=BriefStatus.DECIDE,
            outcome=spec.outcome,
            human_action="unpark (`task` transition) or expire",
            gaps=("parked — a boundary refused a step or a human parked it",),
            subject=task_id,
        )
    if state in (TaskState.REJECTED, TaskState.EXPIRED):
        return OutcomeBrief(
            status=BriefStatus.FAILED,
            outcome=spec.outcome,
            gaps=(f"terminal state: {state.value}",),
            subject=task_id,
        )
    if state is TaskState.RUNNING:
        return OutcomeBrief(
            status=BriefStatus.REVIEW,
            outcome=spec.outcome,
            gaps=("run in flight — a run record will land under runs/",),
            subject=task_id,
        )
    # draft/reviewed/sealed/ready — lifecycle pending
    return OutcomeBrief(
        status=BriefStatus.DECIDE,
        outcome=spec.outcome,
        human_action=f"advance the lifecycle from {state.value}",
        subject=task_id,
    )


def brief_payload(root: Path, task_id: str) -> dict[str, object]:
    try:
        brief = brief_for_task(root, task_id)
    except ContractError:
        raise
    except Exception as exc:
        raise ContractError("AF-BRIEF", f"brief failed for {task_id!r}: {exc}") from exc
    payload = brief.model_dump(mode="json")
    payload["history_len"] = len(store.history(root, task_id))
    return payload


def brief_for_agentic_run(root: Path, task_id: str, run_id: str) -> OutcomeBrief:
    """Render a bounded runtime result without granting task acceptance."""
    run_path = store.task_dir(root, task_id) / "runs" / run_id.replace(":", "-") / "run.json"
    if not run_path.is_file():
        raise ContractError("AF-RUNTIME-NOT-FOUND", f"no runtime run {run_id!r}")
    payload = json.loads(run_path.read_text(encoding="utf-8"))
    spec = store.load(root, task_id)
    status = str(payload.get("final_status", "REVIEW"))
    gaps = tuple(str(item) for item in payload.get("gaps", ()))
    if status == "BLOCKED":
        return OutcomeBrief(status=BriefStatus.BLOCKED, outcome=spec.outcome, gaps=gaps, subject=run_id)
    if status == "DONE":
        return OutcomeBrief(status=BriefStatus.DONE, outcome=spec.outcome, proof=(str(run_path),), subject=run_id)
    return OutcomeBrief(status=BriefStatus.REVIEW, outcome=spec.outcome, gaps=gaps, proof=(str(run_path),), subject=run_id)


def brief_for_grpc_verification(intention: str, verdict: str, evidence: tuple[str, ...], gaps: tuple[str, ...] = ()) -> OutcomeBrief:
    """Render gRPC verification into the same DONE/REVIEW/BLOCKED vocabulary."""
    if verdict == "DONE" and not gaps and evidence:
        return OutcomeBrief(status=BriefStatus.DONE, outcome=intention, proof=evidence, subject="grpc")
    status = BriefStatus.BLOCKED if verdict == "BLOCKED" else BriefStatus.REVIEW
    return OutcomeBrief(status=status, outcome=intention, proof=evidence, gaps=gaps or ("gRPC verification requires review",), subject="grpc")
