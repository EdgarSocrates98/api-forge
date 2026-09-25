"""Persistent AgentOps control plane for bounded local/CI execution."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import ContractError, VersionedContract
from apiforge.core.ids import stable_id
from apiforge.runtime.store import content_hash

StepStatus = Literal["pending", "running", "succeeded", "failed", "cancelled"]
RunStatus = Literal[
    "planned", "running", "awaiting_review", "completed", "failed", "cancelled", "blocked"
]


class ControlStep(VersionedContract):
    step_id: str
    name: str
    dependencies: tuple[str, ...] = ()
    status: StepStatus = "pending"
    attempts: int = 0
    max_retries: int = Field(default=2, ge=0)
    result_sha256: str | None = None
    checkpoint_sha256: str | None = None
    idempotency_key: str | None = None
    result_ref: str | None = None
    error: str | None = None
    lease_owner: str | None = None
    lease_until: str | None = None
    heartbeat_at: str | None = None


class ControlRun(VersionedContract):
    run_id: str
    task_id: str
    status: RunStatus = "planned"
    steps: tuple[ControlStep, ...] = ()
    max_parallel: int = Field(default=4, ge=1, le=64)
    max_calls: int = Field(default=20, ge=1)
    calls_used: int = 0
    reviewer: str | None = None
    review_verdict: Literal["approved", "rejected", "review"] | None = None
    cancellation_actor: str | None = None
    state_revision: int = Field(default=0, ge=0)


class ControlPlane:
    """Small append-only state machine; execution remains outside this class."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.directory = self.root / ".apiforge" / "control"
        self.directory.mkdir(parents=True, exist_ok=True)

    def _directory(self, run_id: str) -> Path:
        return self.directory / run_id.replace(":", "-")

    def _save(self, run: ControlRun) -> None:
        directory = self._directory(run.run_id)
        directory.mkdir(parents=True, exist_ok=True)
        temporary = directory / "run.json.tmp"
        temporary.write_text(
            json.dumps(run.model_dump(mode="json"), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary.replace(directory / "run.json")

    def _event(self, run: ControlRun, event: str, **payload: object) -> None:
        path = self._directory(run.run_id) / "events.jsonl"
        record = {
            "event_id": stable_id(
                "control-event",
                {"run": run.run_id, "event": event, "n": run.calls_used, "payload": payload},
            ),
            "run_id": run.run_id,
            "event": event,
            "payload": payload,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def _load(self, run_id: str) -> ControlRun:
        path = self._directory(run_id) / "run.json"
        if not path.is_file():
            raise ContractError("AF-CONTROL-RUN-NOT-FOUND", run_id)
        return ControlRun.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def create(
        self,
        task_id: str,
        steps: tuple[tuple[str, tuple[str, ...]], ...],
        *,
        max_parallel: int = 4,
        max_calls: int = 20,
        max_retries: int = 2,
        run_id: str | None = None,
    ) -> ControlRun:
        if not steps:
            raise ContractError("AF-CONTROL-STEPS", "at least one step is required")
        names = {name for name, _ in steps}
        if any(dep not in names for _, deps in steps for dep in deps):
            raise ContractError("AF-CONTROL-DEPENDENCY", "step dependency is not declared")
        identifier = run_id or stable_id("control-run", {"task": task_id, "steps": steps})
        run = ControlRun(
            run_id=identifier,
            task_id=task_id,
            max_parallel=max_parallel,
            max_calls=max_calls,
            steps=tuple(
                ControlStep(
                    step_id=stable_id("step", {"run": identifier, "name": name}),
                    name=name,
                    dependencies=deps,
                    max_retries=max_retries,
                    idempotency_key=stable_id(
                        "step-idempotency",
                        {"run": identifier, "name": name, "dependencies": deps},
                    ),
                )
                for name, deps in steps
            ),
        )
        self._save(run)
        self._event(run, "planned", steps=[step.name for step in run.steps])
        return run

    def get(self, run_id: str) -> ControlRun:
        return self._load(run_id)

    def ready(self, run_id: str) -> tuple[ControlStep, ...]:
        run = self._load(run_id)
        completed = {step.name for step in run.steps if step.status == "succeeded"}
        return tuple(
            step
            for step in run.steps
            if step.status == "pending" and all(dep in completed for dep in step.dependencies)
        )

    def plan(self, run_id: str) -> dict[str, object]:
        run = self._load(run_id)
        ready = self.ready(run_id)
        return {
            "run_id": run_id,
            "status": run.status,
            "ready_steps": [step.model_dump(mode="json") for step in ready],
            "parallel_width": min(run.max_parallel, len(ready)),
            "calls_remaining": max(0, run.max_calls - run.calls_used),
        }

    def start(self, run_id: str, step_id: str) -> ControlRun:
        run = self._load(run_id)
        if run.status in {"completed", "cancelled", "blocked"}:
            raise ContractError("AF-CONTROL-TERMINAL", f"run is {run.status}")
        if run.calls_used >= run.max_calls:
            raise ContractError("AF-CONTROL-BUDGET", "max_calls exhausted")
        step = next((item for item in run.steps if item.step_id == step_id), None)
        if step is None:
            raise ContractError("AF-CONTROL-STEP-NOT-FOUND", step_id)
        if step not in self.ready(run_id):
            raise ContractError("AF-CONTROL-NOT-READY", step_id)
        updated = step.model_copy(
            update={
                "status": "running",
                "attempts": step.attempts + 1,
                "error": None,
                "checkpoint_sha256": None,
            }
        )
        steps = tuple(updated if item.step_id == step_id else item for item in run.steps)
        result = run.model_copy(
            update={
                "status": "running",
                "steps": steps,
                "calls_used": run.calls_used + 1,
                "state_revision": run.state_revision + 1,
            }
        )
        self._save(result)
        self._event(result, "step_started", step_id=step_id, attempt=updated.attempts)
        return result

    def claim(
        self,
        run_id: str,
        step_id: str,
        *,
        worker_id: str,
        lease_until: str,
    ) -> ControlRun:
        """Start a ready step and persist ownership for crash recovery."""
        if not worker_id or not lease_until:
            raise ContractError("AF-CONTROL-LEASE", "worker_id and lease_until are required")
        if step_id not in {step.step_id for step in self.ready(run_id)}:
            raise ContractError("AF-CONTROL-NOT-READY", step_id)
        started = self.start(run_id, step_id)
        step = next(item for item in started.steps if item.step_id == step_id)
        claimed = step.model_copy(
            update={
                "lease_owner": worker_id,
                "lease_until": lease_until,
                "heartbeat_at": lease_until,
            }
        )
        result = started.model_copy(
            update={
                "steps": tuple(
                    claimed if item.step_id == step_id else item for item in started.steps
                )
            }
        )
        self._save(result)
        self._event(
            result, "step_claimed", step_id=step_id, worker_id=worker_id, lease_until=lease_until
        )
        return result

    def heartbeat(
        self, run_id: str, step_id: str, *, worker_id: str, lease_until: str
    ) -> ControlRun:
        run = self._load(run_id)
        step = next((item for item in run.steps if item.step_id == step_id), None)
        if step is None or step.status != "running" or step.lease_owner != worker_id:
            raise ContractError("AF-CONTROL-LEASE", "worker does not own the running step")
        updated = step.model_copy(update={"lease_until": lease_until, "heartbeat_at": lease_until})
        result = run.model_copy(
            update={
                "steps": tuple(updated if item.step_id == step_id else item for item in run.steps),
                "state_revision": run.state_revision + 1,
            }
        )
        self._save(result)
        self._event(
            result, "step_heartbeat", step_id=step_id, worker_id=worker_id, lease_until=lease_until
        )
        return result

    def recover_expired(self, run_id: str, *, now: str) -> ControlRun:
        """Return expired running steps to the queue for another worker."""
        run = self._load(run_id)
        current = datetime.fromisoformat(now)
        steps: list[ControlStep] = []
        recovered: list[str] = []
        for step in run.steps:
            expired = False
            if step.status == "running" and step.lease_until:
                expiry = datetime.fromisoformat(step.lease_until)
                expired = expiry <= current
            if expired:
                steps.append(
                    step.model_copy(
                        update={
                            "status": "pending",
                            "lease_owner": None,
                            "lease_until": None,
                            "heartbeat_at": None,
                            "error": "AF-CONTROL-LEASE-EXPIRED",
                        }
                    )
                )
                recovered.append(step.step_id)
            else:
                steps.append(step)
        result = run.model_copy(
            update={
                "status": "running" if recovered else run.status,
                "steps": tuple(steps),
                "state_revision": run.state_revision + (1 if recovered else 0),
            }
        )
        self._save(result)
        if recovered:
            self._event(result, "leases_recovered", step_ids=recovered, now=now)
        return result

    def complete(self, run_id: str, step_id: str, result: object) -> ControlRun:
        run = self._load(run_id)
        step = next((item for item in run.steps if item.step_id == step_id), None)
        if step is None:
            raise ContractError("AF-CONTROL-STEP-STATE", step_id)
        result_digest = content_hash(result)
        if step.status == "succeeded":
            if step.result_sha256 == result_digest:
                return run
            raise ContractError(
                "AF-CONTROL-IDEMPOTENCY-CONFLICT",
                f"step {step_id} already completed with a different result",
            )
        if step.status != "running":
            raise ContractError("AF-CONTROL-STEP-STATE", step_id)
        updated = step.model_copy(
            update={
                "status": "succeeded",
                "result_sha256": result_digest,
                "checkpoint_sha256": result_digest,
                "lease_owner": None,
                "lease_until": None,
                "heartbeat_at": None,
            }
        )
        steps = tuple(updated if item.step_id == step_id else item for item in run.steps)
        terminal_steps = {"succeeded", "skipped", "cancelled"}
        status: RunStatus = (
            "awaiting_review" if all(item.status in terminal_steps for item in steps) else "running"
        )
        result_run = run.model_copy(
            update={"status": status, "steps": steps, "state_revision": run.state_revision + 1}
        )
        self._save(result_run)
        self._event(
            result_run, "step_succeeded", step_id=step_id, result_sha256=updated.result_sha256
        )
        return result_run

    def skip(self, run_id: str, step_id: str, reason: str) -> ControlRun:
        """Mark a planned step as intentionally unused without hiding the reason."""
        run = self._load(run_id)
        step = next((item for item in run.steps if item.step_id == step_id), None)
        if step is None or step.status not in {"pending", "skipped"}:
            raise ContractError("AF-CONTROL-STEP-STATE", step_id)
        if step.status == "skipped" and step.error == reason:
            return run
        updated = step.model_copy(update={"status": "skipped", "error": reason})
        steps = tuple(updated if item.step_id == step_id else item for item in run.steps)
        terminal_steps = {"succeeded", "skipped", "cancelled"}
        status: RunStatus = (
            "awaiting_review" if all(item.status in terminal_steps for item in steps) else run.status
        )
        result = run.model_copy(
            update={"status": status, "steps": steps, "state_revision": run.state_revision + 1}
        )
        self._save(result)
        self._event(result, "step_skipped", step_id=step_id, reason=reason)
        return result

    def fail(self, run_id: str, step_id: str, error: str) -> ControlRun:
        run = self._load(run_id)
        step = next((item for item in run.steps if item.step_id == step_id), None)
        if step is None or step.status != "running":
            raise ContractError("AF-CONTROL-STEP-STATE", step_id)
        retry = step.attempts <= step.max_retries
        updated = step.model_copy(
            update={"status": "pending" if retry else "failed", "error": error}
        )
        status: RunStatus = "running" if retry else "failed"
        result_run = run.model_copy(
            update={
                "status": status,
                "steps": tuple(updated if item.step_id == step_id else item for item in run.steps),
                "state_revision": run.state_revision + 1,
            }
        )
        self._save(result_run)
        self._event(result_run, "step_failed", step_id=step_id, retry_scheduled=retry, error=error)
        return result_run

    def cancel(self, run_id: str, actor: str) -> ControlRun:
        run = self._load(run_id)
        steps = tuple(
            item.model_copy(update={"status": "cancelled"})
            if item.status in {"pending", "running"}
            else item
            for item in run.steps
        )
        result = run.model_copy(
            update={
                "status": "cancelled",
                "steps": steps,
                "cancellation_actor": actor,
                "state_revision": run.state_revision + 1,
            }
        )
        self._save(result)
        self._event(result, "cancelled", actor=actor)
        return result

    def review(
        self, run_id: str, reviewer: str, verdict: Literal["approved", "rejected", "review"]
    ) -> ControlRun:
        run = self._load(run_id)
        if run.status != "awaiting_review":
            raise ContractError("AF-CONTROL-REVIEW-STATE", "run is not awaiting review")
        status: RunStatus = (
            "completed"
            if verdict == "approved"
            else "blocked"
            if verdict == "rejected"
            else "awaiting_review"
        )
        result = run.model_copy(
            update={
                "status": status,
                "reviewer": reviewer,
                "review_verdict": verdict,
                "state_revision": run.state_revision + 1,
            }
        )
        self._save(result)
        self._event(result, "reviewed", reviewer=reviewer, verdict=verdict)
        return result

    def replay(self, run_id: str) -> dict[str, object]:
        run = self._load(run_id)
        path = self._directory(run_id) / "events.jsonl"
        events = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for event in events:
            event.pop("event_id", None)
        return {"run": run.model_dump(mode="json"), "events": events}
