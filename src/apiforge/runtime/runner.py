"""Synchronous host boundary for the agentic runtime."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.routing import RoutingDecision, RoutingPlan
from apiforge.runtime.adapters import FakeModelAdapter, ModelAdapter
from apiforge.runtime.control import ControlPlane
from apiforge.runtime.supervisor import execute_run, resume_existing_run


def run_runtime(
    root: Path,
    task_id: str,
    *,
    adapter: ModelAdapter | None = None,
    policy_id: str = "local-ci-safe",
    now: str | None = None,
    requested_debate: bool = False,
) -> dict[str, object]:
    return asyncio.run(
        execute_run(
            Path(root),
            task_id,
            adapter=adapter or FakeModelAdapter(),
            policy_id=policy_id,
            now=now,
            requested_debate=requested_debate,
        )
    )


def runtime_status(root: Path, task_id: str) -> dict[str, object]:
    """Read the newest indexed runtime run."""
    from apiforge.taskspec.store import latest_run

    latest = latest_run(root, task_id)
    result: dict[str, object] = {"task_id": task_id, "run": latest, "found": latest is not None}
    if isinstance(latest, dict):
        run_id = latest.get("run_id")
        if isinstance(run_id, str):
            run_dir = (
                Path(root)
                / ".apiforge"
                / "tasks"
                / task_id
                / "runs"
                / run_id.replace(":", "-")
            )
            for name, contract in (
                ("routing.json", RoutingDecision),
                ("routing-plan.json", RoutingPlan),
            ):
                path = run_dir / name
                if not path.is_file():
                    continue
                try:
                    value = contract.model_validate(json.loads(path.read_text(encoding="utf-8")))
                except (OSError, UnicodeDecodeError, ValueError) as exc:
                    errors = result.get("routing_errors")
                    if not isinstance(errors, list):
                        errors = []
                        result["routing_errors"] = errors
                    errors.append(f"{name}: {exc}")
                else:
                    result["routing_plan" if name == "routing-plan.json" else "routing"] = (
                        value.model_dump(mode="json")
                    )
    if isinstance(latest, dict) and latest.get("control_run_id"):
        try:
            control = ControlPlane(root).get(str(latest["control_run_id"]))
        except ContractError as exc:
            result["control_error"] = str(exc)
        else:
            result["control"] = control.model_dump(mode="json")
    return result


def approve_runtime(root: Path, task_id: str, run_id: str, approver: str) -> dict[str, object]:
    """Record a human approval as an auditable local artifact."""
    from datetime import UTC, datetime

    from apiforge.runtime.store import RunStore

    gate = {
        "run_id": run_id,
        "task_id": task_id,
        "approver": approver,
        "decision": "approved",
        "approved_at": datetime.now(UTC).isoformat(),
    }
    path = RunStore(root, task_id, run_id).json("approval.json", gate)
    return {"approved": True, "path": str(path), **gate}


def resume_runtime(
    root: Path, task_id: str, *, policy_id: str = "local-ci-safe"
) -> dict[str, object]:
    """Resume only persisted, eligible work from the latest control run."""
    from apiforge.taskspec.store import latest_run

    latest = latest_run(root, task_id)
    if latest is None:
        raise ContractError("AF-RUNTIME-NOT-FOUND", f"no runtime run for {task_id!r}")
    run_id = latest.get("control_run_id") or latest.get("run_id")
    if not isinstance(run_id, str) or not latest.get("control_run_id"):
        return {
            "task_id": task_id,
            "status": "REVIEW",
            "resumed": False,
            "gaps": ("AF-RUNTIME-COMPATIBILITY: legacy run has no control record",),
            "run": latest,
        }
    return asyncio.run(
        resume_existing_run(
            Path(root),
            task_id,
            run_id,
            adapter=FakeModelAdapter(),
            policy_id=policy_id,
        )
    )


def debate_runtime(
    root: Path, task_id: str, *, policy_id: str = "local-ci-safe"
) -> dict[str, object]:
    """Request a human-visible debate room for the next bounded run."""
    return run_runtime(root, task_id, policy_id=policy_id, requested_debate=True)
