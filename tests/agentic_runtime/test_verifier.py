from pathlib import Path

from apiforge.contracts.verification import HoldoutRecord
from apiforge.taskspec.planner import plan_task
from apiforge.verification.service import verify_project, verify_task


def test_project_checks_cover_four_proof_axes(orders_paths: dict[str, Path]) -> None:
    checks = verify_project(orders_paths["contract"], orders_paths["project"])
    assert {check.axis for check in checks} == {
        "contract", "security", "idempotency", "pagination"
    }
    assert all(check.verdict == "pass" for check in checks)


def test_missing_project_is_inconclusive(orders_paths: dict[str, Path], tmp_path: Path) -> None:
    checks = verify_project(orders_paths["contract"], tmp_path / "missing")
    assert checks[0].verdict == "inconclusive"


def test_verification_requires_detected_holdouts(
    sealed_task: tuple[Path, str], orders_paths: dict[str, Path]
) -> None:
    root, task_id = sealed_task
    plan_task(root, task_id)
    holdout = tuple(
        HoldoutRecord(
            mutation_id=f"mutation-{axis}",
            target="app.py",
            expected_axis=axis,
            detected=True,
            evidence=(f"holdout:{axis}",),
        )
        for axis in ("security", "idempotency", "pagination")
    )
    record = verify_task(
        root,
        task_id,
        project=orders_paths["project"],
        contract=orders_paths["contract"],
        holdout=holdout,
    )
    assert record.verdict == "pass"
    assert len(record.checks) == 4
