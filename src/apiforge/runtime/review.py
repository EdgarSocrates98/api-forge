"""Semantic review of a TaskSpec before an agentic run starts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal, cast

from apiforge.contracts.agentic import RuntimeReview
from apiforge.contracts.task import TaskSpec, TaskState
from apiforge.core.ids import stable_id


def review_task_spec(root: Path, spec: TaskSpec) -> tuple[dict[str, object], ...]:
    findings: list[dict[str, object]] = []
    if spec.state not in {TaskState.SEALED, TaskState.READY, TaskState.RUNNING}:
        findings.append(
            {
                "code": "AF-RUNTIME-TASK-STATE",
                "message": f"task must be sealed or ready, got {spec.state.value}",
                "severity": "high",
            }
        )
    if not spec.outcome.strip():
        findings.append(
            {"code": "AF-RUNTIME-TASK-OUTCOME", "message": "outcome is empty", "severity": "high"}
        )
    if not spec.expected_proofs:
        findings.append(
            {
                "code": "AF-RUNTIME-TASK-PROOF",
                "message": "expected_proofs is empty",
                "severity": "high",
            }
        )
    if not spec.acceptance_criteria:
        findings.append(
            {
                "code": "AF-RUNTIME-TASK-ACCEPTANCE",
                "message": "acceptance_criteria is empty",
                "severity": "high",
            }
        )
    if not spec.rollback.strip():
        findings.append(
            {"code": "AF-RUNTIME-TASK-ROLLBACK", "message": "rollback is empty", "severity": "high"}
        )
    for item in spec.inputs:
        key, sep, value = item.partition("=")
        if (
            sep
            and key in {"project", "contract", "case", "input_path"}
            and not Path(value).exists()
        ):
            findings.append(
                {
                    "code": "AF-RUNTIME-TASK-INPUT",
                    "message": f"missing input {key}={value}",
                    "severity": "high",
                }
            )
    if (
        spec.risk.value in {"external_mutation", "destructive", "irreversible"}
        and not spec.writable_paths
    ):
        findings.append(
            {
                "code": "AF-RUNTIME-TASK-PATHS",
                "message": "mutating risk has no writable paths",
                "severity": "high",
            }
        )
    return tuple(findings)


def build_runtime_review(
    root: Path, spec: TaskSpec, *, reviewer: str = "api-task-spec-reviewer"
) -> RuntimeReview:
    findings = review_task_spec(root, spec)
    blocked = any(item.get("severity") == "high" for item in findings)
    status = "blocked" if blocked else "review" if findings else "approved"
    content = spec.model_dump(mode="json")
    digest = hashlib.sha256(
        json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return RuntimeReview(
        review_id=stable_id(
            "runtime-review", {"task": spec.id, "revision": spec.revision, "digest": digest}
        ),
        task_id=spec.id,
        revision=spec.revision,
        reviewer=reviewer,
        status=cast(Literal["approved", "review", "blocked"], status),
        finding_codes=tuple(str(item["code"]) for item in findings),
        finding_messages=tuple(str(item["message"]) for item in findings),
        content_sha256=digest,
    )
