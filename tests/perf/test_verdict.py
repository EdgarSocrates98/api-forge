"""perf verdict — passed/failed/inconclusive over a PerformanceRun."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from apiforge.contracts.stubs import PerformanceRun, WorkloadProfile
from apiforge.perf.verdict import verdict


def _complete_run(**over: object) -> PerformanceRun:
    fields: dict[str, object] = {
        "id": "run-1",
        "subject": "orders-api",
        "test_kind": "load",
        "baseline_ref": "run-0",
        "environment": "staging",
        "commit_sha": "abc123",
        "infrastructure_revision": "tf-42",
        "test_duration_s": 600.0,
        "min_duration_s": 300.0,
        "target_tps": 100.0,
        "achieved_tps": 102.0,
        "tps_completed_transactions": True,
        "generator_dropped_iterations": 0,
        "downstreams_observed": True,
        "error_rate": 0.001,
        "slo_error_rate": 0.01,
        "p99_ms": 240.0,
        "slo_p99_ms": 500.0,
        "duplicates_detected": False,
    }
    fields.update(over)
    return PerformanceRun.model_validate(fields)


def _status(report: object, cid: str) -> str:
    return next(c.status for c in report.conditions if c.id == cid)  # type: ignore[attr-defined]


def test_complete_run_passes() -> None:
    report = verdict(_complete_run())
    assert report.verdict == "passed"
    assert all(c.status == "met" for c in report.conditions)


def test_missing_baseline_is_inconclusive() -> None:
    report = verdict(_complete_run(baseline_ref=None))
    assert report.verdict == "inconclusive"
    assert _status(report, "baseline-exists") == "unmet"


def test_generator_saturation_is_inconclusive_not_failed() -> None:
    report = verdict(_complete_run(generator_dropped_iterations=120))
    assert report.verdict == "inconclusive"
    assert _status(report, "generator-not-saturated") == "unmet"


def test_generator_unobserved_is_unevaluable() -> None:
    report = verdict(_complete_run(generator_dropped_iterations=None))
    assert report.verdict == "inconclusive"
    assert _status(report, "generator-not-saturated") == "unevaluable"


def test_target_not_reached_is_inconclusive() -> None:
    report = verdict(_complete_run(achieved_tps=80.0))
    assert report.verdict == "inconclusive"
    assert _status(report, "target-reached") == "unmet"


def test_tps_not_completed_transactions_is_inconclusive() -> None:
    report = verdict(_complete_run(tps_completed_transactions=False))
    assert report.verdict == "inconclusive"
    assert _status(report, "tps-is-completed-transactions") == "unmet"


def test_error_rate_breach_fails() -> None:
    report = verdict(_complete_run(error_rate=0.05))
    assert report.verdict == "failed"
    assert _status(report, "error-rate-within-slo") == "unmet"


def test_p99_breach_fails() -> None:
    report = verdict(_complete_run(p99_ms=900.0))
    assert report.verdict == "failed"
    assert _status(report, "p99-within-slo") == "unmet"


def test_duplicates_fail() -> None:
    report = verdict(_complete_run(duplicates_detected=True))
    assert report.verdict == "failed"
    assert _status(report, "no-duplicate-transactions") == "unmet"


def test_short_test_is_inconclusive() -> None:
    report = verdict(_complete_run(test_duration_s=60.0, min_duration_s=300.0))
    assert report.verdict == "inconclusive"
    assert _status(report, "duration-reported") == "unmet"


def test_slo_absent_is_unevaluable_not_passed() -> None:
    report = verdict(_complete_run(slo_error_rate=None))
    assert report.verdict == "inconclusive"
    assert _status(report, "error-rate-within-slo") == "unevaluable"


def test_test_kind_is_closed_vocabulary() -> None:
    with pytest.raises(ValidationError):
        PerformanceRun.model_validate({"id": "r", "test_kind": "endurance"})
    run = _complete_run(test_kind="soak")
    assert verdict(run).test_kind == "soak"


def test_workload_profile_closed_vocab() -> None:
    profile = WorkloadProfile.model_validate(
        {
            "id": "wp-1",
            "subject": "orders-api",
            "timing": "synchronous",
            "arrival": "bursty",
            "state": "stateless",
            "bound": "io",
            "latency_sensitive": True,
            "scope": "regional",
            "exposure": "public",
        }
    )
    assert profile.timing == "synchronous" and profile.bound == "io"
    # absent dimensions stay None — named absence, never defaulted
    assert profile.multi_tenant is None
    with pytest.raises(ValidationError):
        WorkloadProfile.model_validate({"id": "wp-2", "timing": "eventually"})
