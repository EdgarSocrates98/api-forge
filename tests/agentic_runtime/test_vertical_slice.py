from pathlib import Path

from apiforge.brief.render import brief_for_task
from apiforge.contracts.task import BriefStatus
from apiforge.taskspec.planner import plan_task
from apiforge.taskspec.runner import accept_task, run_task
from apiforge.verification.holdout import run_holdouts
from apiforge.verification.service import verify_task


def test_intent_to_verified_brief(
    sealed_task: tuple[Path, str], orders_paths: dict[str, Path]
) -> None:
    root, task_id = sealed_task
    plan_task(root, task_id)
    run = run_task(root, task_id, "af-executor", now="2026-09-22T00:00:00Z")
    assert run["terminal"] == "awaiting_supervision"
    holdout = run_holdouts(
        root,
        orders_paths["project"],
        orders_paths["contract"],
        orders_paths["manifest"],
    )
    record = verify_task(
        root,
        task_id,
        project=orders_paths["project"],
        contract=orders_paths["contract"],
        run_id="0",
        holdout=holdout,
    )
    assert record.verdict == "pass"
    accept_task(root, task_id, "reviewer", evidence=("verification.json",))
    assert brief_for_task(root, task_id).status is BriefStatus.DONE
