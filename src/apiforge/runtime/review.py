"""Semantic review of a TaskSpec before an agentic run starts."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.task import TaskSpec, TaskState


def review_task_spec(root: Path, spec: TaskSpec) -> tuple[dict[str, object], ...]:
    findings: list[dict[str, object]] = []
    if spec.state not in {TaskState.SEALED, TaskState.READY, TaskState.RUNNING}:
        findings.append({
            "code": "AF-RUNTIME-TASK-STATE",
            "message": f"task must be sealed or ready, got {spec.state.value}",
            "severity": "high",
        })
    if not spec.outcome.strip():
        findings.append({"code": "AF-RUNTIME-TASK-OUTCOME", "message": "outcome is empty", "severity": "high"})
    if not spec.expected_proofs:
        findings.append({"code": "AF-RUNTIME-TASK-PROOF", "message": "expected_proofs is empty", "severity": "high"})
    if not spec.acceptance_criteria:
        findings.append({"code": "AF-RUNTIME-TASK-ACCEPTANCE", "message": "acceptance_criteria is empty", "severity": "high"})
    if not spec.rollback.strip():
        findings.append({"code": "AF-RUNTIME-TASK-ROLLBACK", "message": "rollback is empty", "severity": "high"})
    for item in spec.inputs:
        key, sep, value = item.partition("=")
        if sep and key in {"project", "contract", "case", "input_path"} and not Path(value).exists():
            findings.append({
                "code": "AF-RUNTIME-TASK-INPUT",
                "message": f"missing input {key}={value}",
                "severity": "high",
            })
    if spec.risk.value in {"external_mutation", "destructive", "irreversible"} and not spec.writable_paths:
        findings.append({"code": "AF-RUNTIME-TASK-PATHS", "message": "mutating risk has no writable paths", "severity": "high"})
    return tuple(findings)
