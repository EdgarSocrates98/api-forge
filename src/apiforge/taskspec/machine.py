"""The task state machine — a closed map; illegal transitions are refused."""

from __future__ import annotations

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import TaskState

TRANSITIONS: dict[TaskState, frozenset[TaskState]] = {
    TaskState.DRAFT: frozenset({TaskState.REVIEWED}),
    TaskState.REVIEWED: frozenset({TaskState.SEALED, TaskState.DRAFT}),
    TaskState.SEALED: frozenset({TaskState.READY, TaskState.DRAFT}),
    TaskState.READY: frozenset({TaskState.RUNNING, TaskState.PARKED}),
    TaskState.RUNNING: frozenset(
        {
            TaskState.AWAITING_SUPERVISION,
            TaskState.PARKED,
            TaskState.BLOCKED,
            TaskState.EXPIRED,
        }
    ),
    TaskState.PARKED: frozenset({TaskState.READY, TaskState.EXPIRED}),
    TaskState.AWAITING_SUPERVISION: frozenset(
        {TaskState.ACCEPTED, TaskState.REJECTED, TaskState.RUNNING}
    ),
    TaskState.BLOCKED: frozenset({TaskState.READY, TaskState.EXPIRED}),
    TaskState.ACCEPTED: frozenset(),
    TaskState.REJECTED: frozenset({TaskState.DRAFT}),
    TaskState.EXPIRED: frozenset(),
}


def can_transition(current: TaskState, target: TaskState) -> bool:
    return target in TRANSITIONS.get(current, frozenset())


def require_transition(current: TaskState, target: TaskState) -> None:
    if not can_transition(current, target):
        raise ContractError(
            "AF-TASK-TRANSITION",
            f"cannot move task from {current.value} to {target.value}",
        )
