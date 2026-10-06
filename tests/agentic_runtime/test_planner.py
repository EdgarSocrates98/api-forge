from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.taskspec.planner import build_plan, load_plan, plan_task
from apiforge.taskspec.store import load


def test_plan_is_closed_and_persisted(sealed_task: tuple[Path, str]) -> None:
    root, task_id = sealed_task
    plan = plan_task(root, task_id)
    assert plan.revision == load(root, task_id).revision
    assert plan.plan_digest and len(plan.plan_digest) == 64
    assert all(step["verb"] for step in plan.steps)
    assert load_plan(root, task_id).plan_digest == plan.plan_digest


def test_plan_refuses_unsealed_task(orders_paths: dict[str, Path], tmp_path: Path) -> None:
    from apiforge.taskspec.compiler import compile_intent

    spec = compile_intent(
        "orders-unsealed",
        "verify orders",
        contract=orders_paths["contract"],
        project=orders_paths["project"],
        case=tmp_path,
    )
    with pytest.raises(ContractError, match="AF-TASK-PLAN-UNSEALED"):
        build_plan(spec)
