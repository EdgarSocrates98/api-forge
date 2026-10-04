from __future__ import annotations

from pathlib import Path

from apiforge.contracts.agentic_governance import BudgetLimit, BudgetSpend
from apiforge.contracts.economy import CostVector
from apiforge.governance.budget import build_plan, check_budget, persist_plan, record_spend


def _plan(root: Path, *, token_limit: int | None = None):
    limits = [
        BudgetLimit(scope="task", scope_id="task-1", max_calls=2),
        BudgetLimit(scope="phase", scope_id="build", max_calls=1),
    ]
    if token_limit is not None:
        limits = [BudgetLimit(scope="task", scope_id="task-1", max_observed_tokens=token_limit)]
    plan = build_plan(task_id="task-1", limits=tuple(limits), created_at="2026-10-04T12:00:00Z")
    persist_plan(root, plan)
    return plan


def _spend(plan_id: str, spend_id: str, phase: str = "build", tokens: int | None = None) -> BudgetSpend:
    return BudgetSpend(
        spend_id=spend_id, plan_id=plan_id, task_id="task-1", phase=phase,
        role="builder", tool="compile", cost=CostVector(observed_tokens=tokens),
        observed_at="2026-10-04T12:01:00Z", provenance=("test",),
    )


def test_hierarchy_stops_phase_before_root_and_then_stops_root(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    first = record_spend(tmp_path, plan, _spend(plan.plan_id, "spend-1"))
    assert first.action == "allow" and first.recorded is True
    phase_stop = check_budget(
        tmp_path, plan, task_id="task-1", phase="build", role="builder", tool="compile",
        cost=CostVector(), spend_id="spend-2",
    )
    assert phase_stop.action == "stop"
    second = record_spend(tmp_path, plan, _spend(plan.plan_id, "spend-2", phase="verify"))
    assert second.action == "allow" and second.recorded is True
    root_stop = record_spend(tmp_path, plan, _spend(plan.plan_id, "spend-3", phase="verify"))
    assert root_stop.action == "stop" and "task-1.calls" in root_stop.exhausted


def test_token_limit_is_unresolved_without_observed_tokens(tmp_path: Path) -> None:
    plan = _plan(tmp_path, token_limit=4)
    unknown = check_budget(
        tmp_path, plan, task_id="task-1", phase="build", role="builder", tool="compile",
        cost=CostVector(), spend_id="spend-1",
    )
    assert unknown.action == "unresolved"
    assert unknown.code == "AF-BUDGET-TOKENS-UNRESOLVED"
    measured = record_spend(tmp_path, plan, _spend(plan.plan_id, "spend-1", tokens=4))
    assert measured.action == "allow" and measured.recorded is True
    exhausted = record_spend(tmp_path, plan, _spend(plan.plan_id, "spend-2", tokens=1))
    assert exhausted.code == "AF-BUDGET-EXHAUSTED"


def test_duplicate_spend_is_idempotent(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    spend = _spend(plan.plan_id, "spend-1")
    assert record_spend(tmp_path, plan, spend).recorded is True
    duplicate = record_spend(tmp_path, plan, spend)
    assert duplicate.action == "deduplicated"
