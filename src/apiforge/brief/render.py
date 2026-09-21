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

from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import BriefStatus, OutcomeBrief, TaskState
from apiforge.taskspec import store


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
