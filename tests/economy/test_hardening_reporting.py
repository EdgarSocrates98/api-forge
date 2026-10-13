from pathlib import Path

from apiforge.context.delta import _runtime_path
from apiforge.contracts.economy_evals import EconomyMatrix
from apiforge.economy.phase_budget import plan_phase_budgets
from apiforge.evals.agentic_quality import CLAIM_SCOPE
from apiforge.runtime.adapters import FakeModelAdapter
from apiforge.runtime.runner import run_runtime
from tests.runtime.economy_support import TASK_ID, economy_task


def test_protected_overrun_is_not_reported_as_plain_ok() -> None:
    protected = plan_phase_budgets("economy", usage={"verify": {"calls": 9}})
    assert protected.quality_status == "ok"
    assert protected.budget_status == "protected_overrun"
    exceeded = plan_phase_budgets("economy", usage={"build": {"calls": 9}})
    assert (exceeded.quality_status, exceeded.budget_status) == ("unresolved", "exceeded")
    within = plan_phase_budgets("balanced", usage={"build": {"calls": 1}})
    assert within.budget_status == "ok"


def test_unmapped_runtime_files_degrade_delta_but_docs_do_not() -> None:
    assert _runtime_path("src/payment/service.py")
    assert _runtime_path("openapi.yaml")
    assert not _runtime_path("docs/guide.md")
    assert not _runtime_path("README.md")


def test_routing_unresolved_reaches_the_run_summary(tmp_path: Path) -> None:
    economy_task(tmp_path)
    result = run_runtime(
        tmp_path, TASK_ID, adapter=FakeModelAdapter(), now="2026-09-28T00:00:00+00:00"
    )
    assert "routing" in result["unresolved"]
    summary = (Path(str(result["run_dir"])) / "summary.json").read_text(encoding="utf-8")
    assert '"routing"' in summary


def test_claims_are_scoped() -> None:
    assert EconomyMatrix(tasks=0).claim_scope == "deterministic-safety-economy"
    assert CLAIM_SCOPE == "recorded-agentic-outputs"
