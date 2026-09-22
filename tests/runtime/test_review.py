from pathlib import Path

from apiforge.contracts.task import TaskSpec, TaskState
from apiforge.runtime.review import review_task_spec


def test_review_names_missing_task_proofs(tmp_path: Path) -> None:
    findings = review_task_spec(tmp_path, TaskSpec(id="x", outcome="x", state=TaskState.SEALED))
    assert {item["code"] for item in findings} >= {"AF-RUNTIME-TASK-PROOF", "AF-RUNTIME-TASK-ACCEPTANCE"}
