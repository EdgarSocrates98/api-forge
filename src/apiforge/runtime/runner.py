"""Synchronous host boundary for the agentic runtime."""

from __future__ import annotations

import asyncio
from pathlib import Path

from apiforge.runtime.adapters import FakeModelAdapter, ModelAdapter
from apiforge.runtime.supervisor import execute_run


def run_runtime(
    root: Path,
    task_id: str,
    *,
    adapter: ModelAdapter | None = None,
    policy_id: str = "local-ci-safe",
    now: str | None = None,
    requested_debate: bool = False,
) -> dict[str, object]:
    return asyncio.run(execute_run(
        Path(root),
        task_id,
        adapter=adapter or FakeModelAdapter(),
        policy_id=policy_id,
        now=now,
        requested_debate=requested_debate,
    ))


def runtime_status(root: Path, task_id: str) -> dict[str, object]:
    """Read the newest indexed runtime run."""
    from apiforge.taskspec.store import latest_run

    latest = latest_run(root, task_id)
    return {"task_id": task_id, "run": latest, "found": latest is not None}


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


def resume_runtime(root: Path, task_id: str, *, policy_id: str = "local-ci-safe") -> dict[str, object]:
    """Replay the task through the same bounded supervisor policy."""
    return run_runtime(root, task_id, policy_id=policy_id)


def debate_runtime(root: Path, task_id: str, *, policy_id: str = "local-ci-safe") -> dict[str, object]:
    """Request a human-visible debate room for the next bounded run."""
    return run_runtime(root, task_id, policy_id=policy_id, requested_debate=True)
