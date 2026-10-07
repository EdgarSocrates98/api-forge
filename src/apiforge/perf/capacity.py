"""Deterministic capacity assessment over an already measured performance run."""

from __future__ import annotations

from typing import Literal, cast

from apiforge.contracts.stubs import CapacityAssessment, PerformanceRun
from apiforge.perf.verdict import verdict


def assess_capacity(
    run: PerformanceRun,
    *,
    headroom_pct: float | None = 20.0,
) -> CapacityAssessment:
    """Build a capacity envelope without inventing missing measurements.

    The assessment delegates validity and SLO semantics to ``perf.verdict``.
    A safe TPS envelope is emitted only for a passing run and a valid,
    explicitly declared headroom percentage.
    """

    if headroom_pct is not None and not 0 <= headroom_pct < 100:
        raise ValueError("headroom_pct must be in [0, 100)")

    report = verdict(run)
    blockers = tuple(
        f"{condition.id}:{condition.detail}"
        for condition in report.conditions
        if condition.status != "met"
    )
    evidence = tuple(condition.id for condition in report.conditions if condition.status == "met")
    status = cast(
        Literal["passed", "failed", "inconclusive"],
        report.verdict,
    )
    max_safe_tps = None
    if status == "passed" and run.achieved_tps is not None and headroom_pct is not None:
        max_safe_tps = round(run.achieved_tps * (1 - headroom_pct / 100), 6)
        evidence = (*evidence, "declared-headroom")

    return CapacityAssessment(
        id=f"capacity-{run.id}",
        subject=run.subject,
        source_run_id=run.id,
        status=status,
        target_tps=run.target_tps,
        achieved_tps=run.achieved_tps,
        max_safe_tps=max_safe_tps,
        headroom_pct=headroom_pct,
        blockers=blockers,
        evidence=evidence,
    )
