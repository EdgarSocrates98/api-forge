"""Execute a task's recipe within budgets; the record is evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import AcceptanceRecord, TaskSpec, TaskState
from apiforge.dispatch.runner import (
    DispatchContext,
    _need,
    dispatch_step,
    is_mutation_verb,
    required_fields,
)
from apiforge.taskspec import store
from apiforge.taskspec.machine import require_transition
from apiforge.taskspec.service import _parse_inputs, load_recipes


def _ctx_for(root: Path, spec: TaskSpec, now: str | None) -> DispatchContext:
    fields = _parse_inputs(spec)
    if now is not None:
        fields["now"] = now
    case = fields.pop("case", store.task_dir(root, spec.id))
    fields.pop("gate_detail", None)  # consumed by the mutation gate, not a ctx field
    return DispatchContext(case=Path(case), **fields)


def _mutation_step(
    verb: str, spec: TaskSpec, ctx: DispatchContext
) -> dict[str, object]:
    """Policy-gate a mutation verb, then run it — sandbox-scoped, never promote.

    Two conditions, both named when absent: the policy engine must allow the
    action (class ``local_reversible``, gate fields from ``gate.*`` inputs),
    and the task must declare ``writable_paths`` covering the sandbox dir —
    mutation writes never leave ``.apiforge``.
    """
    from apiforge.policy.decide import ActionRequest, decide
    from apiforge.policy.loader import load_policy

    entry: dict[str, object] = {"verb": verb}
    gate_detail = _parse_inputs(spec).get("gate_detail") or {}
    decision = decide(
        load_policy(),
        ActionRequest(
            verb="build.endpoint",
            autonomy_class="local_reversible",
            args=(ctx.operation_id or "",),
            target=str(ctx.project or ""),
            detail=gate_detail,
        ),
    )
    entry["policy_decision"] = decision.model_dump(mode="json")
    writable = tuple(spec.writable_paths)
    if not any(p.startswith(".apiforge") for p in writable):
        entry["status"] = "refused"
        entry["reason"] = (
            "AF-TASK-MUTATION-GATED: writable_paths lacks a .apiforge scope"
        )
        return entry
    if decision.outcome != "allow":
        entry["status"] = "refused"
        entry["reason"] = (
            f"policy {decision.outcome}: "
            f"{decision.reason_code or ''} {list(decision.missing_requirements)}"
        )
        return entry
    return entry | dispatch_step(verb, ctx, allow_mutation=True)


def run_task(
    root: Path,
    task_id: str,
    actor: str,
    now: str | None = None,
) -> dict[str, object]:
    """Run the recipe inside the task's budgets.

    Terminal states: all steps ran -> ``awaiting_supervision``; a refused
    verb (policy/dispatch boundary) -> ``parked``; missing inputs or errors
    -> ``blocked``; a round with zero ran steps -> ``blocked`` (no-progress
    breaker); deadline exceeded -> ``expired``.
    """
    spec = store.load(root, task_id)
    if spec.state is TaskState.SEALED:
        # auto-advance through ready, binding the run to the sealed revision
        spec = _mark_ready(root, spec)
    require_transition(spec.state, TaskState.RUNNING)
    spec = spec.model_copy(update={"state": TaskState.RUNNING})
    store.write_spec(store.task_dir(root, task_id), spec)
    store.record_event(root, task_id, {"event": "->running", "by": actor})

    budgets = spec.budgets
    if budgets.deadline and now is not None and now > budgets.deadline:
        return _finish(root, spec, actor, TaskState.EXPIRED, "deadline exceeded", [])

    recipe = load_recipes().get(spec.strategy.value)
    if recipe is None:
        raise ContractError(
            "AF-TASK-RECIPE", f"no recipe {spec.strategy.value!r} in recipes.yaml"
        )

    ctx = _ctx_for(root, spec, now)
    inputs_missing = sorted({
        field
        for verb in recipe
        for field in _need(ctx, *required_fields(verb))
    })
    calls = 0
    all_steps: list[dict[str, object]] = []
    rounds = 0
    stop: str | None = None
    for round_no in range(1, budgets.max_rounds + 1):
        rounds = round_no
        ran_this_round = 0
        for verb in recipe:
            if calls >= budgets.max_calls:
                stop = "max_calls exhausted"
                break
            if is_mutation_verb(verb):
                entry = _mutation_step(verb, spec, ctx)
            else:
                entry = dispatch_step(verb, ctx)
            entry["round"] = round_no
            all_steps.append(entry)
            calls += 1
            if entry["status"] == "ran":
                ran_this_round += 1
        if stop:
            break
        if ran_this_round == 0:
            stop = "no progress"
            break
        # a full clean round is enough — retrying would only repeat work
        if all(s["status"] == "ran" for s in all_steps if s.get("round") == round_no):
            break

    statuses = {s["status"] for s in all_steps}
    if stop == "no progress":
        terminal, reason = TaskState.BLOCKED, "round ended with zero ran steps"
    elif stop == "max_calls exhausted":
        terminal, reason = TaskState.EXPIRED, stop
    elif "refused" in statuses:
        terminal, reason = TaskState.PARKED, "a step was refused at a boundary"
    elif "error" in statuses or "pending" in statuses:
        terminal, reason = TaskState.BLOCKED, "steps pending or errored"
    else:
        terminal, reason = TaskState.AWAITING_SUPERVISION, "all steps ran"
    return _finish(
        root, spec, actor, terminal, reason, all_steps,
        rounds=rounds, calls=calls, inputs_missing=inputs_missing,
    )


def _mark_ready(root: Path, spec: TaskSpec) -> TaskSpec:
    from apiforge.taskspec.service import _revision

    require_transition(spec.state, TaskState.READY)
    revision = _revision(root, spec.id, spec.revision)
    if revision.seal_signature_b64 is None:
        raise ContractError(
            "AF-TASK-UNSEALED",
            f"revision {revision.revision} is not sealed — run `task seal` first",
        )
    spec = spec.model_copy(update={"state": TaskState.READY})
    store.write_spec(store.task_dir(root, spec.id), spec)
    store.record_event(root, spec.id, {"event": "->ready", "revision": spec.revision})
    return spec


def _finish(
    root: Path,
    spec: TaskSpec,
    actor: str,
    terminal: TaskState,
    reason: str,
    steps: list[dict[str, object]],
    *,
    rounds: int = 0,
    calls: int = 0,
    inputs_missing: list[str] | None = None,
) -> dict[str, object]:
    require_transition(spec.state, terminal)
    spec = spec.model_copy(update={"state": terminal})
    store.write_spec(store.task_dir(root, spec.id), spec)
    record: dict[str, object] = {
        "task_id": spec.id,
        "revision": spec.revision,
        "executed_by": actor,
        "terminal": terminal.value,
        "reason": reason,
        "inputs_missing": inputs_missing or [],
        "rounds": rounds,
        "calls": calls,
        "steps": steps,
    }
    path = store.record_run(root, spec.id, record)
    store.record_event(
        root, spec.id, {"event": f"->{terminal.value}", "by": actor, "reason": reason}
    )
    return record | {"run_record": str(path)}


def _last_run(root: Path, task_id: str) -> dict[str, Any] | None:
    runs = sorted(store.task_dir(root, task_id).joinpath("runs").glob("*.json"))
    if not runs:
        return None
    data: dict[str, Any] = json.loads(runs[-1].read_text(encoding="utf-8"))
    return data


def accept_task(
    root: Path,
    task_id: str,
    actor: str,
    evidence: tuple[str, ...] = (),
    notes: str = "",
) -> dict[str, object]:
    """Accept a supervised run — the acceptor is never the executor."""
    spec = store.load(root, task_id)
    require_transition(spec.state, TaskState.ACCEPTED)
    run = _last_run(root, task_id) or {}
    record = AcceptanceRecord(
        task_id=task_id,
        revision=spec.revision,
        verdict="accepted",
        accepted_by=actor,
        executed_by=run.get("executed_by"),
        evidence=evidence,
        notes=notes,
    )
    spec = spec.model_copy(update={"state": TaskState.ACCEPTED})
    store.write_spec(store.task_dir(root, task_id), spec)
    store.record_event(
        root,
        task_id,
        {
            "event": "->accepted",
            "by": actor,
            "executed_by": run.get("executed_by"),
            "evidence": list(evidence),
        },
    )
    return record.model_dump(mode="json")


def reject_task(root: Path, task_id: str, actor: str, reason: str) -> TaskSpec:
    spec = store.load(root, task_id)
    require_transition(spec.state, TaskState.REJECTED)
    return _transition_via(root, spec, TaskState.REJECTED, {"by": actor, "reason": reason})


def park_task(root: Path, task_id: str, actor: str, reason: str) -> TaskSpec:
    spec = store.load(root, task_id)
    require_transition(spec.state, TaskState.PARKED)
    return _transition_via(root, spec, TaskState.PARKED, {"by": actor, "reason": reason})


def expire_task(root: Path, task_id: str, actor: str, reason: str) -> TaskSpec:
    spec = store.load(root, task_id)
    require_transition(spec.state, TaskState.EXPIRED)
    return _transition_via(root, spec, TaskState.EXPIRED, {"by": actor, "reason": reason})


def _transition_via(
    root: Path, spec: TaskSpec, target: TaskState, event: dict[str, Any]
) -> TaskSpec:
    spec = spec.model_copy(update={"state": target})
    store.write_spec(store.task_dir(root, spec.id), spec)
    store.record_event(root, spec.id, {"event": f"->{target.value}", **event})
    return spec


def task_status(root: Path, task_id: str) -> dict[str, object]:
    spec = store.load(root, task_id)
    return {
        "task": spec.model_dump(mode="json"),
        "history": store.history(root, task_id),
    }
