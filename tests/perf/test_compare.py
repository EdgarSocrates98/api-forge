"""perf compare — compare_runs / detect_regression over PerformanceRun."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.otel.extract import extract_otel
from apiforge.adapters.otel.run import build_performance_run
from apiforge.perf.compare import compare_runs, detect_regression

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "otel"


def _run(name: str):
    return build_performance_run(extract_otel(FIXTURE / name), name)


def test_regression_detected_on_post() -> None:
    report = compare_runs(_run("baseline.json"), _run("candidate.json"))
    assert report.compared == 2
    reg = {(r.operation, r.metric) for r in report.regressions}
    assert ("POST /orders", "mean_ms") in reg
    assert ("POST /orders", "p95_ms") in reg
    post = next(
        r for r in report.regressions if r.operation == "POST /orders" and r.metric == "mean_ms"
    )
    assert post.delta_pct > 40.0


def test_no_false_positive_on_stable_op() -> None:
    report = compare_runs(_run("baseline.json"), _run("candidate.json"))
    get_regs = [r for r in report.regressions if r.operation == "GET /orders/{id}"]
    assert get_regs == []


def test_added_and_insufficient_named() -> None:
    report = compare_runs(_run("baseline.json"), _run("candidate.json"))
    assert "GET /orders/search" in report.added
    # absent from baseline -> named as added, never compared or judged
    assert report.removed == ()


def test_insufficient_samples_named_not_judged() -> None:
    report = compare_runs(_run("baseline.json"), _run("candidate.json"), min_samples=6)
    assert set(report.insufficient_data) == {"GET /orders/{id}", "POST /orders"}
    assert report.regressions == ()


def test_threshold_is_declared() -> None:
    huge = compare_runs(_run("baseline.json"), _run("candidate.json"), threshold_pct=200.0)
    assert huge.regressions == ()
    strict = compare_runs(_run("baseline.json"), _run("candidate.json"), threshold_pct=1.0)
    # POST still fires at a strict threshold; GET did not regress at all
    assert any(r.operation == "POST /orders" for r in strict.regressions)
    assert not any(r.operation == "GET /orders/{id}" for r in strict.regressions)


def test_detect_regression_matches_compare() -> None:
    regs = detect_regression(_run("baseline.json"), _run("candidate.json"))
    assert regs == compare_runs(_run("baseline.json"), _run("candidate.json")).regressions


def test_self_compare_no_regressions() -> None:
    report = compare_runs(_run("baseline.json"), _run("baseline.json"))
    assert report.regressions == ()
    assert report.compared == 2


def test_removed_operations_named() -> None:
    report = compare_runs(_run("candidate.json"), _run("baseline.json"))
    assert "GET /orders/search" in report.removed
