"""TaskSpec factory for economy-routing tests."""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.task import TaskRisk, TaskSize, TaskSpec, TaskState
from apiforge.taskspec.store import create

TASK_ID = "evolve-orders-api"


def economy_task(
    root: Path,
    *,
    risk: TaskRisk = TaskRisk.READ_ONLY,
    size: TaskSize = TaskSize.M,
    max_calls: int = 20,
) -> TaskSpec:
    project = root / "project"
    project.mkdir(parents=True, exist_ok=True)
    (project / "openapi.yaml").write_text("openapi: 3.0.0\n", encoding="utf-8")
    spec = TaskSpec(
        id=TASK_ID,
        outcome="produce a reviewed API evolution plan",
        size=size,
        inputs=(f"project={project}",),
        expected_proofs=("specialist artifact",),
        acceptance_criteria=("all findings are evidence bound",),
        rollback="discard local run artifacts",
        risk=risk,
        state=TaskState.SEALED,
        revision=1,
        budgets={"max_calls": max_calls},
    )
    return create(root, spec)


def record_deterministic_run(
    root: Path,
    *,
    output: str,
    terminal: str = "awaiting_supervision",
    proof_kind: str | None = None,
    tamper: bool = False,
) -> None:
    """Record a task run; ``proof_kind`` attaches a structured, hashed ProofReceipt."""
    import hashlib

    runs = root / ".apiforge" / "tasks" / TASK_ID / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    step: dict[str, object] = {"verb": "verify", "status": "ran", "output": output}
    if proof_kind is not None:
        artifact = runs / "proof-artifact.json"
        artifact.write_text(json.dumps({"verdict": "verified"}), encoding="utf-8")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if tamper:
            artifact.write_text(json.dumps({"verdict": "forged"}), encoding="utf-8")
        step["proofs"] = [
            {
                "proof_id": "proof-1",
                "kind": proof_kind,
                "sha256": digest,
                "artifact_ref": artifact.relative_to(root).as_posix(),
            }
        ]
    (runs / "0.json").write_text(
        json.dumps({"task_id": TASK_ID, "terminal": terminal, "steps": [step]}),
        encoding="utf-8",
    )
