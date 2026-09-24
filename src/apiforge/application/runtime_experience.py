"""Canonical application services for the friendly runtime experience."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.runtime.runner import (
    debate_runtime,
    resume_runtime,
    run_runtime,
    runtime_status,
)
from apiforge.taskspec import store as task_store


def doctor(root: Path, task_id: str) -> dict[str, object]:
    status = runtime_status(root, task_id)
    if not status["found"]:
        raise ContractError("AF-RUNTIME-NOT-FOUND", f"no runtime run for {task_id!r}")
    run = status.get("run")
    checks = {
        "run_persisted": True,
        "control_persisted": bool(isinstance(run, dict) and run.get("control_run_id")),
        "terminal_proof": bool(isinstance(run, dict) and run.get("run_digest")),
        "gaps_declared": bool(isinstance(run, dict) and "gaps" in run),
    }
    unresolved = tuple(name for name, passed in checks.items() if not passed)
    run_payload = run if isinstance(run, dict) else {}
    return {
        "command": "doctor",
        "task_id": task_id,
        "status": "REVIEW" if unresolved else str(run_payload.get("final_status", "REVIEW")),
        "checks": checks,
        "gaps": unresolved,
        "runtime": status,
    }


def status(root: Path, task_id: str) -> dict[str, object]:
    return {"command": "status", **runtime_status(root, task_id)}


def review(root: Path, task_id: str) -> dict[str, object]:
    from apiforge.brief.render import brief_for_agentic_run, brief_payload

    latest = task_store.latest_run(root, task_id)
    if latest is None:
        return {"command": "review", "brief": brief_payload(root, task_id)}
    run_id = latest.get("run_id")
    if not isinstance(run_id, str):
        raise ContractError("AF-RUNTIME-COMPATIBILITY", "latest run has no run_id")
    brief = brief_for_agentic_run(root, task_id, run_id)
    return {"command": "review", "brief": brief.model_dump(mode="json"), "run": latest}


def evolve(
    root: Path,
    task_id: str,
    *,
    policy_id: str = "local-ci-safe",
    now: str | None = None,
    requested_debate: bool = False,
) -> dict[str, object]:
    return {
        "command": "evolve",
        **run_runtime(
            root,
            task_id,
            policy_id=policy_id,
            now=now,
            requested_debate=requested_debate,
        ),
    }


def resume(root: Path, task_id: str, *, policy_id: str = "local-ci-safe") -> dict[str, object]:
    return {"command": "resume", **resume_runtime(root, task_id, policy_id=policy_id)}


def debate(root: Path, task_id: str, *, policy_id: str = "local-ci-safe") -> dict[str, object]:
    return {"command": "debate", **debate_runtime(root, task_id, policy_id=policy_id)}


def cancel(root: Path, task_id: str, *, actor: str = "tui-user") -> dict[str, object]:
    """Cancel through the ControlPlane facade; presentation never writes stores."""
    from apiforge.runtime.control import ControlPlane

    current = runtime_status(root, task_id)
    run = current.get("run")
    control_run_id = run.get("control_run_id") if isinstance(run, dict) else None
    if not isinstance(control_run_id, str):
        raise ContractError("AF-CONTROL-RUN-NOT-FOUND", f"no control run for {task_id!r}")
    return {
        "command": "cancel",
        "task_id": task_id,
        "run": ControlPlane(root).cancel(control_run_id, actor).model_dump(mode="json"),
    }
