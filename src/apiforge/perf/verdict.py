"""Deterministic verdict over a PerformanceRun.

The verdict vocabulary is the closed set from the run contract:
``passed``, ``failed``, ``inconclusive`` (``blocked``,
``skipped_with_reason``, ``unsafe_to_run``, ``not_applicable`` are
declared by whoever produced the run — a verdict is computed only over
a run that exists).

A run is ``passed`` only when every *validity* condition is met **and**
every *performance* condition is met. A validity condition that cannot
be evaluated — the run never reported the field — makes the verdict
``inconclusive`` and names the missing evidence; it is never guessed.
A performance condition that is unmet fails the run. Nothing here
interpolates or assumes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

from apiforge.contracts.stubs import PerformanceRun


class Condition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    status: str  # met | unmet | unevaluable
    detail: str


class VerdictReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    verdict: str  # passed | failed | inconclusive
    subject: str
    test_kind: str | None
    conditions: tuple[Condition, ...]


def _cond(cid: str, status: str, detail: str) -> Condition:
    return Condition(id=cid, status=status, detail=detail)


def _present(value: Any) -> bool:
    return value is not None


def _noise_condition(
    run: PerformanceRun, repeat_baselines: tuple[PerformanceRun, ...]
) -> Condition | None:
    """Is the candidate distinguishable from repeated-baseline noise?

    Only evaluated when repeated baseline runs are supplied. Every shared
    run-level field must differ from the baseline mean by more than its
    measured floor for the run to be distinguishable; otherwise the
    difference may be environment noise and the verdict must not pretend
    otherwise.
    """
    from apiforge.perf.noise import RUN_FIELDS, field_noise

    if not repeat_baselines:
        return None
    within: list[str] = []
    proven = False
    for field_name in RUN_FIELDS:
        candidate = getattr(run, field_name, None)
        if not isinstance(candidate, (int, float)):
            continue
        info = field_noise(list(repeat_baselines), field_name)
        floor = info["floor"]
        if floor is None or info["n"] < 2:
            continue
        proven = True
        values = [
            float(v)
            for r in repeat_baselines
            if isinstance((v := getattr(r, field_name, None)), (int, float))
        ]
        mean = sum(values) / len(values)
        delta = abs(float(candidate) - mean) / abs(mean) if mean else float("inf")
        if delta <= floor:
            within.append(f"{field_name} delta {delta * 100:.2f}% <= floor {floor * 100:.2f}%")
    if not proven:
        return _cond(
            "distinguishable-from-baseline",
            "unevaluable",
            "noise floor unproven — no field with >=2 repeated observations",
        )
    if within and len(within) == sum(
        1
        for f in RUN_FIELDS
        if isinstance(getattr(run, f, None), (int, float))
        and field_noise(list(repeat_baselines), f)["n"] >= 2
    ):
        return _cond(
            "distinguishable-from-baseline",
            "unevaluable",
            "every observed delta is inside the measured noise floor: " + "; ".join(within),
        )
    return _cond(
        "distinguishable-from-baseline",
        "met",
        "at least one delta exceeds the measured noise floor"
        + (f"; within-floor: {'; '.join(within)}" if within else ""),
    )


def _validity_conditions(
    run: PerformanceRun,
    repeat_baselines: tuple[PerformanceRun, ...] = (),
) -> list[Condition]:
    """Conditions whose absence or failure makes the run inconclusive."""
    conds: list[Condition] = []
    noise = _noise_condition(run, repeat_baselines)
    if noise is not None:
        conds.append(noise)

    conds.append(
        _cond(
            "baseline-exists",
            "met" if run.baseline_ref else "unmet",
            "baseline_ref declared" if run.baseline_ref else "no baseline_ref",
        )
    )
    conds.append(
        _cond(
            "environment-identified",
            "met" if run.environment else "unmet",
            f"environment={run.environment!r}",
        )
    )
    reproducible = run.commit_sha and run.infrastructure_revision
    conds.append(
        _cond(
            "scenario-reproducible",
            "met" if reproducible else "unmet",
            "commit_sha + infrastructure_revision declared"
            if reproducible
            else "commit_sha or infrastructure_revision missing",
        )
    )
    duration, min_duration = run.test_duration_s, run.min_duration_s
    if duration is None:
        conds.append(_cond("duration-reported", "unevaluable", "test_duration_s absent"))
    elif min_duration is not None and duration < min_duration:
        conds.append(
            _cond(
                "duration-reported",
                "unmet",
                f"test_duration_s={duration} < declared min {min_duration}",
            )
        )
    else:
        conds.append(_cond("duration-reported", "met", f"test_duration_s={duration}"))
    target, achieved = run.target_tps, run.achieved_tps
    if target is None or achieved is None:
        conds.append(
            _cond(
                "target-reached",
                "unevaluable",
                "target_tps or achieved_tps absent",
            )
        )
    elif achieved < target:
        conds.append(
            _cond(
                "target-reached",
                "unmet",
                f"achieved_tps={achieved} < target_tps={target}",
            )
        )
    else:
        conds.append(
            _cond(
                "target-reached",
                "met",
                f"achieved_tps={achieved} >= target_tps={target}",
            )
        )
    dropped = run.generator_dropped_iterations
    if dropped is None:
        conds.append(
            _cond(
                "generator-not-saturated",
                "unevaluable",
                "generator_dropped_iterations absent — the generator was not observed",
            )
        )
    elif dropped > 0:
        conds.append(
            _cond(
                "generator-not-saturated",
                "unmet",
                f"generator dropped {dropped} iterations — it was the bottleneck",
            )
        )
    else:
        conds.append(_cond("generator-not-saturated", "met", "no dropped iterations"))
    conds.append(
        _cond(
            "downstreams-observed",
            "met"
            if run.downstreams_observed
            else ("unevaluable" if run.downstreams_observed is None else "unmet"),
            "downstreams_observed declared"
            if run.downstreams_observed is not None
            else "downstreams_observed absent",
        )
    )
    conds.append(
        _cond(
            "tps-is-completed-transactions",
            "met"
            if run.tps_completed_transactions
            else ("unevaluable" if run.tps_completed_transactions is None else "unmet"),
            "tps counts completed business transactions"
            if run.tps_completed_transactions
            else "TPS metric does not provably count completed transactions",
        )
    )
    return conds


def _performance_conditions(run: PerformanceRun) -> list[Condition]:
    """Conditions whose failure fails the run — all thresholds declared."""
    conds: list[Condition] = []
    error_rate, slo_error = run.error_rate, run.slo_error_rate
    if error_rate is None or slo_error is None:
        conds.append(
            _cond(
                "error-rate-within-slo",
                "unevaluable",
                "error_rate or slo_error_rate absent",
            )
        )
    elif error_rate <= slo_error:
        conds.append(
            _cond(
                "error-rate-within-slo",
                "met",
                f"error_rate={error_rate} <= slo {slo_error}",
            )
        )
    else:
        conds.append(
            _cond(
                "error-rate-within-slo",
                "unmet",
                f"error_rate={error_rate} > slo {slo_error}",
            )
        )
    p99, slo_p99 = run.p99_ms, run.slo_p99_ms
    if p99 is None or slo_p99 is None:
        conds.append(_cond("p99-within-slo", "unevaluable", "p99_ms or slo_p99_ms absent"))
    elif p99 <= slo_p99:
        conds.append(_cond("p99-within-slo", "met", f"p99_ms={p99} <= slo {slo_p99}"))
    else:
        conds.append(
            _cond(
                "p99-within-slo",
                "unmet",
                f"p99_ms={p99} > slo {slo_p99}",
            )
        )
    conds.append(
        _cond(
            "no-duplicate-transactions",
            "met"
            if run.duplicates_detected is False
            else ("unevaluable" if run.duplicates_detected is None else "unmet"),
            "duplicates_detected declared"
            if run.duplicates_detected is not None
            else "duplicates_detected absent",
        )
    )
    return conds


def verdict(
    run: PerformanceRun,
    repeat_baselines: tuple[PerformanceRun, ...] = (),
) -> VerdictReport:
    """Evaluate a run: passed / failed / inconclusive, conditions named."""
    validity = _validity_conditions(run, repeat_baselines)
    perf = _performance_conditions(run)
    all_conds = validity + perf
    if any(c.status != "met" for c in validity):
        result = "inconclusive"
    elif any(c.status != "met" for c in perf):
        result = "failed" if any(c.status == "unmet" for c in perf) else "inconclusive"
    else:
        result = "passed"
    return VerdictReport(
        verdict=result,
        subject=run.subject,
        test_kind=run.test_kind,
        conditions=tuple(all_conds),
    )
