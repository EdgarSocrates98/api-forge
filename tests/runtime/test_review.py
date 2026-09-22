from pathlib import Path

from apiforge.contracts.task import TaskSpec, TaskState
from apiforge.runtime.review import build_runtime_review, review_task_spec


def test_review_names_missing_task_proofs(tmp_path: Path) -> None:
    findings = review_task_spec(tmp_path, TaskSpec(id="x", outcome="x", state=TaskState.SEALED))
    assert {item["code"] for item in findings} >= {"AF-RUNTIME-TASK-PROOF", "AF-RUNTIME-TASK-ACCEPTANCE"}


def test_runtime_review_is_digest_bound_and_blocked_on_high_findings(tmp_path: Path) -> None:
    review = build_runtime_review(tmp_path, TaskSpec(id="x", outcome="x", state=TaskState.SEALED))

    assert review.status == "blocked"
    assert review.reviewer == "api-task-spec-reviewer"
    assert len(review.content_sha256) == 64
