"""Autonomy service — evaluate actions, record them, maybe run them.

Every evaluated action lands in ``ledger.jsonl`` (append-only): the record
names the mode, the policy decision (rule, missing requirements), and the
outcome — ``observed``, ``executed``, ``pending``, ``denied``, ``skipped``
or ``error``. ``executed`` entries carry the canonical output hash. Only
verbs in the dispatch table can ever execute; everything else is recorded
as ``not_dispatchable`` — autonomy never reaches outside that boundary.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.autonomy.modes import (
    AutonomyError,
    AutonomyMode,
    ModeState,
    autonomy_dir,
    load_mode,
)
from apiforge.core.yaml import StrictLoadError, load_yaml_mapping
from apiforge.dispatch.runner import DispatchContext, _match_verb, dispatch_step
from apiforge.policy.decide import ActionRequest, decide
from apiforge.policy.models import Policy

_LEDGER = "ledger.jsonl"


def _ledger_path(root: Path) -> Path:
    return autonomy_dir(root) / _LEDGER


def append_ledger(root: Path, entry: dict[str, Any]) -> Path:
    path = _ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(entry, sort_keys=True, separators=(",", ":"), default=str)
            + "\n"
        )
    return path


def read_ledger(root: Path) -> list[dict[str, Any]]:
    path = _ledger_path(root)
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def set_mode(
    root: Path,
    target: AutonomyMode,
    *,
    actor: str,
    now: str | None,
    reason: str,
    policy: Policy,
    detail: dict[str, str],
    requested: str | None = None,
) -> ModeState:
    """Change the mode — the change itself is a ``sensitive`` policy action.

    Escalating to ``observe`` is the exception the shipped policy allows by
    rule; everything else flows through ``decide`` and is refused when its
    gate requirements are not supplied in ``detail``.
    """
    current = load_mode(root).mode
    decision = decide(
        policy,
        ActionRequest(
            verb="autonomy.set",
            autonomy_class="sensitive",
            args=(target.value,),
            target=target.value,
            detail=detail,
        ),
    )
    entry = {
        "event": "mode.set",
        "from": current.value,
        "to": target.value,
        "actor": actor,
        "at": now,
        "decision": decision.outcome,
        "rule": decision.rule,
        "missing": list(decision.missing_requirements),
    }
    if requested is not None and requested != target.value:
        # v1 vocabulary accepted via V1_MODE_MAP — the mapping is recorded
        entry["requested"] = requested
    if decision.outcome != "allow":
        entry["result"] = "refused"
        append_ledger(root, entry)
        raise AutonomyError(
            "AF-AUTONOMY-SET-REFUSED",
            f"{current.value} -> {target.value} refused ({decision.outcome}); "
            f"missing: {list(decision.missing_requirements)}",
        )
    state = ModeState(mode=target, set_by=actor, set_at=now, reason=reason)
    path = autonomy_dir(root) / "mode.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    entry["result"] = "applied"
    append_ledger(root, entry)
    return state


def run_action(
    root: Path,
    verb: str,
    *,
    action_class: str,
    args: tuple[str, ...],
    target: str | None,
    detail: dict[str, str],
    ctx: DispatchContext,
    policy: Policy,
    actor: str = "",
    now: str | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Evaluate one action under the current mode; execute only on ``allow``.

    ``observe`` records the decision as ``observed`` and never runs. A
    ``gate`` decision is recorded ``pending`` with its missing requirements.
    ``deny`` is recorded and refused. ``allow`` runs through the dispatch
    table — unknown or ``collect *`` verbs are recorded ``not_dispatchable``.
    """
    mode = load_mode(root).mode
    _, _, extra = _match_verb(verb)
    entry: dict[str, Any] = {
        "event": "action",
        "verb": verb,
        "class": action_class,
        "mode": mode.value,
        "actor": actor,
        "at": now,
    }
    if extra in ("__unknown__", "__collect__"):
        entry["outcome"] = "not_dispatchable"
        if record:
            append_ledger(root, entry)
        return entry
    decision = decide(
        policy,
        ActionRequest(
            verb=verb,
            autonomy_class=action_class,
            args=args,
            target=target,
            detail=detail,
        ),
    )
    entry["decision"] = decision.outcome
    entry["rule"] = decision.rule
    entry["missing"] = list(decision.missing_requirements)
    if mode is AutonomyMode.OBSERVE:
        entry["outcome"] = "observed"
    elif decision.outcome == "deny":
        entry["outcome"] = "denied"
    elif decision.outcome == "gate":
        entry["outcome"] = "pending"
    else:
        step = dispatch_step(verb, ctx)
        if step["status"] == "ran":
            entry["outcome"] = "executed"
            entry["output_sha256"] = step["output_sha256"]
        elif step["status"] == "pending":
            entry["outcome"] = "pending"
            entry["missing_inputs"] = step.get("missing", [])
        else:
            entry["outcome"] = step["status"]  # refused | error
            if "error" in step:
                entry["error"] = step["error"]
    if record:
        append_ledger(root, entry)
    return entry


class RunbookError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def load_runbooks() -> dict[str, dict[str, Any]]:
    from importlib import resources

    text = (
        resources.files("apiforge.rules")
        .joinpath("runbooks.yaml")
        .read_text(encoding="utf-8")
    )
    try:
        data = load_yaml_mapping(text, source="runbooks.yaml")
    except StrictLoadError as exc:
        raise RunbookError("AF-AUTONOMY-RUNBOOK-SCHEMA", str(exc)) from exc
    runbooks = data.get("runbooks")
    if not isinstance(runbooks, dict):
        raise RunbookError("AF-AUTONOMY-RUNBOOK-SCHEMA", "missing 'runbooks' map")
    for name, spec in runbooks.items():
        if not isinstance(spec, dict) or not isinstance(spec.get("steps"), list):
            raise RunbookError(
                "AF-AUTONOMY-RUNBOOK-SCHEMA", f"{name}: missing 'steps' list"
            )
    return dict(runbooks)


def run_runbook(
    root: Path,
    name: str,
    *,
    ctx: DispatchContext,
    policy: Policy,
    detail: dict[str, str],
    actor: str = "",
    now: str | None = None,
) -> dict[str, Any]:
    """Run a runbook's steps under the current mode.

    ``observe`` walks every step recording decisions; ``supervised`` halts
    on the first non-executed step; ``continuous`` records the skip and
    keeps going.
    """
    runbooks = load_runbooks()
    spec = runbooks.get(name)
    if spec is None:
        raise RunbookError(
            "AF-AUTONOMY-RUNBOOK-UNKNOWN",
            f"no runbook {name!r}; known: {sorted(runbooks)}",
        )
    mode = load_mode(root).mode
    steps: list[dict[str, Any]] = []
    halted = False
    for order, step in enumerate(spec["steps"], 1):
        if halted:
            steps.append({"order": order, "verb": step.get("verb"),
                          "outcome": "not_reached"})
            continue
        verb = str(step.get("verb", ""))
        action_class = str(step.get("class", "read_only"))
        entry = run_action(
            root,
            verb,
            action_class=action_class,
            args=tuple(step.get("args") or ()),
            target=step.get("target"),
            detail=detail,
            ctx=ctx,
            policy=policy,
            actor=actor,
            now=now,
        )
        steps.append({"order": order, **entry})
        if mode is AutonomyMode.SUPERVISED and entry["outcome"] != "executed":
            halted = True
    executed = sum(1 for s in steps if s["outcome"] == "executed")
    result = {
        "runbook": name,
        "mode": mode.value,
        "executed": executed,
        "halted": halted,
        "steps": steps,
    }
    append_ledger(root, {"event": "runbook", **{k: result[k] for k in
                                               ("runbook", "mode", "executed", "halted")},
                         "actor": actor, "at": now})
    return result


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
