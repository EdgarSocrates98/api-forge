from apiforge.contracts.stubs import PerformanceRun
from apiforge.perf_control import assess_run, build_plan


def test_plan_is_external_execution_safe() -> None:
    plan = build_plan("orders", ("POST /orders",), target_tps=100)

    assert plan.execution_allowed is False
    assert plan.generator == "k6"


def test_assessment_passes_only_with_complete_evidence() -> None:
    plan = build_plan("orders", ("POST /orders",), target_tps=100)
    result = assess_run(
        plan,
        PerformanceRun(
            id="run-1",
            subject="orders",
            achieved_tps=120,
            p99_ms=200,
            error_rate=0.001,
            generator_dropped_iterations=0,
            downstreams_observed=True,
        ),
    )

    assert result.verdict == "PASS"
    assert result.external_execution is False


def test_assessment_refuses_missing_metrics_as_inconclusive() -> None:
    plan = build_plan("orders", ("POST /orders",), target_tps=100)

    result = assess_run(plan, PerformanceRun(id="run-2", subject="orders", achieved_tps=100))

    assert result.verdict == "INCONCLUSIVE"
    assert "p99_ms" in result.missing_evidence
