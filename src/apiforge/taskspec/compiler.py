"""Compile a bounded local API intention into a TaskSpec draft."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import Recipe, TaskRisk, TaskSize, TaskSpec


def compile_intent(
    task_id: str,
    outcome: str,
    *,
    contract: Path,
    project: Path,
    case: Path,
    writable_paths: tuple[str, ...] = (".apiforge",),
) -> TaskSpec:
    """Create a closed, local-only task draft from explicit artifact paths."""
    for label, path in (("contract", contract), ("project", project), ("case", case)):
        if not Path(path).exists():
            raise ContractError("AF-TASK-CONTEXT", f"{label} does not exist: {path}")
    return TaskSpec(
        id=task_id,
        outcome=outcome,
        size=TaskSize.M,
        writable_paths=writable_paths,
        inputs=(
            f"contract={contract}",
            f"project={project}",
            f"case={case}",
        ),
        preconditions=("contract exists", "project exists", "case is local"),
        tests=("contract", "security", "idempotency", "pagination"),
        expected_proofs=("verification record", "detected holdout", "receipt"),
        risk=TaskRisk.LOCAL_REVERSIBLE,
        strategy=Recipe.VERIFIED_API_SLICE,
        rollback="remove the task sandbox and evidence directory",
        acceptance_criteria=(
            "all required proof axes pass",
            "all declared holdouts are detected",
            "acceptance is recorded by a distinct actor",
        ),
        capability_covered="agentic-api-verification",
    )
