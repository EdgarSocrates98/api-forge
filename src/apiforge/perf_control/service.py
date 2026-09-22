"""Performance plan composition and closed-world run assessment."""

from __future__ import annotations

from typing import Literal

from apiforge.contracts.stubs import PerformanceRun
from apiforge.perf_control.models import PerformanceAssessment, PerformancePlan


def build_plan(
    subject: str,
    endpoints: tuple[str, ...],
    *,
    target_tps: float,
    test_kind: str = "load",
    duration_s: int = 60,
    warmup_s: int = 10,
    max_error_rate: float = 0.01,
    max_p99_ms: float = 500,
    generator: str = "k6",
) -> PerformancePlan:
    if not endpoints:
        raise ValueError("AF-PERF-PLAN-ENDPOINTS: at least one endpoint is required")
    return PerformancePlan(
        subject=subject,
        endpoints=tuple(sorted(set(endpoints))),
        target_tps=target_tps,
        test_kind=test_kind,  # type: ignore[arg-type]
        duration_s=duration_s,
        warmup_s=warmup_s,
        max_error_rate=max_error_rate,
        max_p99_ms=max_p99_ms,
        generator=generator,  # type: ignore[arg-type]
    )


def assess_run(plan: PerformancePlan, run: PerformanceRun) -> PerformanceAssessment:
    """Assess only declared measurements; absence is inconclusive, never zero."""
    missing: list[str] = []
    failed: list[str] = []
    if run.achieved_tps is None:
        missing.append("achieved_tps")
    elif run.achieved_tps < plan.target_tps:
        failed.append(f"achieved_tps {run.achieved_tps} < target {plan.target_tps}")
    if run.p99_ms is None:
        missing.append("p99_ms")
    elif run.p99_ms > plan.max_p99_ms:
        failed.append(f"p99_ms {run.p99_ms} > limit {plan.max_p99_ms}")
    if run.error_rate is None:
        missing.append("error_rate")
    elif run.error_rate > plan.max_error_rate:
        failed.append(f"error_rate {run.error_rate} > limit {plan.max_error_rate}")
    if run.generator_dropped_iterations is None:
        missing.append("generator_dropped_iterations")
    elif run.generator_dropped_iterations > 0:
        failed.append("generator_dropped_iterations > 0")
    if run.downstreams_observed is None:
        missing.append("downstreams_observed")
    elif not run.downstreams_observed:
        failed.append("downstreams_observed is false")
    verdict: Literal["PASS", "FAIL", "INCONCLUSIVE"] = (
        "FAIL" if failed else "INCONCLUSIVE" if missing else "PASS"
    )
    return PerformanceAssessment(
        subject=run.subject or plan.subject,
        verdict=verdict,
        target_tps=plan.target_tps,
        achieved_tps=run.achieved_tps,
        p99_ms=run.p99_ms,
        error_rate=run.error_rate,
        failed_conditions=tuple(failed),
        missing_evidence=tuple(missing),
    )
