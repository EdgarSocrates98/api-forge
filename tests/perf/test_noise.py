"""Noise floor — measured variance, honest inconclusive (AT-002)."""

from pathlib import Path

import pytest

from apiforge.contracts.stubs import PerformanceRun
from apiforge.perf.compare import compare_runs
from apiforge.perf.noise import field_noise, metric_noise, noise_floor
from apiforge.perf.verdict import verdict


def _run(subject: str, p99: float, err: float, **kw: object) -> PerformanceRun:
    return PerformanceRun.model_validate(
        {
            "id": f"{subject}-{p99}-{err}",
            "subject": subject,
            "p99_ms": p99,
            "error_rate": err,
            **kw,
        }
    )


def test_floor_needs_two_observations() -> None:
    assert noise_floor([1.0]) is None
    assert noise_floor([]) is None
    assert noise_floor([100.0, 102.0]) == pytest.approx(2 / 101)


def test_zero_mean_floor() -> None:
    assert noise_floor([0.0, 0.0]) == 0.0
    assert noise_floor([-1.0, 1.0]) is None  # mean zero with spread: undefined


def test_field_noise_reports_n() -> None:
    runs = [_run("s", 100, 0.01), _run("s", 102, 0.011)]
    info = field_noise(runs, "p99_ms")
    assert info["n"] == 2
    assert info["floor"] == pytest.approx(2 / 101)
    assert field_noise(runs[:1], "p99_ms")["floor"] is None


def test_metric_noise_pools_operations() -> None:
    ops = {"op": {"mean_ms": 100.0}}
    runs = [
        PerformanceRun.model_validate({"id": "a", "attributes": {"operations": ops}}),
        PerformanceRun.model_validate(
            {"id": "b", "attributes": {"operations": {"op": {"mean_ms": 104.0}}}}
        ),
    ]
    assert metric_noise(runs, "mean_ms")["floor"] == pytest.approx(4 / 102)


def test_at002_delta_within_floor_is_inconclusive(tmp_path: Path) -> None:
    """3 baselines ~±2% variance; candidate +1.5% -> inconclusive naming floor."""
    baselines = tuple(
        _run("orders", p99, err) for p99, err in ((100.0, 0.010), (102.0, 0.0102), (98.0, 0.0098))
    )
    candidate = _run("orders", 101.5, 0.01015)
    report = verdict(candidate, repeat_baselines=baselines)
    cond = next(c for c in report.conditions if c.id == "distinguishable-from-baseline")
    assert cond.status == "unevaluable"
    assert "floor" in cond.detail
    assert report.verdict == "inconclusive"


def test_delta_beyond_floor_is_distinguishable() -> None:
    baselines = tuple(
        _run("orders", p99, err) for p99, err in ((100.0, 0.010), (102.0, 0.0102), (98.0, 0.0098))
    )
    candidate = _run("orders", 150.0, 0.010)
    report = verdict(candidate, repeat_baselines=baselines)
    cond = next(c for c in report.conditions if c.id == "distinguishable-from-baseline")
    assert cond.status == "met"


def test_single_baseline_leaves_floor_unproven() -> None:
    report = verdict(_run("orders", 150.0, 0.02), repeat_baselines=(_run("o", 100, 0.01),))
    cond = next(c for c in report.conditions if c.id == "distinguishable-from-baseline")
    assert cond.status == "unevaluable"
    assert "unproven" in cond.detail


def test_compare_suppresses_regression_inside_floor() -> None:
    base_ops = {"GET /a": {"count": 5, "mean_ms": 100.0}}
    cand_ops = {"GET /a": {"count": 5, "mean_ms": 112.0}}
    baseline = PerformanceRun.model_validate({"id": "b", "attributes": {"operations": base_ops}})
    candidate = PerformanceRun.model_validate({"id": "c", "attributes": {"operations": cand_ops}})
    repeats = tuple(
        PerformanceRun.model_validate(
            {
                "id": f"r{i}",
                "attributes": {"operations": {"GET /a": {"count": 5, "mean_ms": v}}},
            }
        )
        for i, v in enumerate((90.0, 110.0, 100.0))
    )
    report = compare_runs(
        baseline,
        candidate,
        threshold_pct=10.0,
        min_samples=3,
        repeat_baselines=repeats,
    )
    assert report.regressions == ()
    assert len(report.below_noise_floor) == 1
    assert report.below_noise_floor[0].operation == "GET /a"
    # without repeats the same delta is a regression
    plain = compare_runs(baseline, candidate, threshold_pct=10.0, min_samples=3)
    assert len(plain.regressions) == 1
