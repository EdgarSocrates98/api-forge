"""Bind a sealed TaskSpec to a closed, persisted TaskPlan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import TaskPlan, TaskSpec, TaskState
from apiforge.core.models import JsonValue
from apiforge.taskspec import store
from apiforge.taskspec.service import load_recipes

_AXES = ("contract", "security", "idempotency", "pagination")


def _digest(plan: TaskPlan) -> str:
    payload = json.dumps(plan.model_dump(mode="json"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_plan(spec: TaskSpec) -> TaskPlan:
    if spec.state not in {TaskState.SEALED, TaskState.READY}:
        raise ContractError("AF-TASK-PLAN-UNSEALED", "plan requires a sealed revision")
    verbs = load_recipes().get(spec.strategy.value)
    if not verbs:
        raise ContractError("AF-TASK-PLAN-RECIPE", f"no recipe for {spec.strategy.value!r}")
    steps: list[dict[str, JsonValue]] = []
    for index, verb in enumerate(verbs, start=1):
        steps.append(
            {
                "id": f"step-{index:02d}",
                "verb": verb,
                "inputs": tuple(spec.inputs),
                "writable_paths": tuple(spec.writable_paths),
                "expected_artifacts": (f"step-{index:02d}.json",),
                "proof_axes": _AXES if verb in {"judge", "verify task"} else (),
                "risk": spec.risk.value,
            }
        )
    plan = TaskPlan(
        task_id=spec.id,
        revision=spec.revision,
        recipe=spec.strategy,
        steps=tuple(steps),
        proof_axes=_AXES,
    )
    return plan.model_copy(update={"plan_digest": _digest(plan)})


def plan_task(root: Path, task_id: str) -> TaskPlan:
    spec = store.load(root, task_id)
    plan = build_plan(spec)
    path = store.task_dir(root, task_id) / "plan.json"
    path.write_text(
        json.dumps(plan.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8"
    )
    store.record_event(
        root,
        task_id,
        {
            "event": "planned",
            "revision": spec.revision,
            "plan_digest": plan.plan_digest,
        },
    )
    return plan


def load_plan(root: Path, task_id: str) -> TaskPlan:
    path = store.task_dir(root, task_id) / "plan.json"
    if not path.is_file():
        raise ContractError("AF-TASK-PLAN-MISSING", f"no plan for task {task_id!r}")
    return TaskPlan.model_validate(json.loads(path.read_text(encoding="utf-8")))
