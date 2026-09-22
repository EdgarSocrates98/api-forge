"""Load-tool report readers — locust/jmeter/gatling/vegeta/wrk/hey/pytest-benchmark."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.testreports import (
    extract_gatling,
    extract_hey,
    extract_jmeter,
    extract_locust,
    extract_pytest_benchmark,
    extract_vegeta,
    extract_wrk,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "reports"


def test_locust_aggregated_row() -> None:
    inv = extract_locust(FIXTURES / "locust-stats.csv")
    fact = inv.facts[0]
    assert fact.measures["requests"] == 1000
    assert fact.measures["failures"] == 5
    assert fact.attrs["rps"] == 33.3
    assert fact.attrs["p99_ms"] == 210


def test_jmeter_aggregates_samples() -> None:
    inv = extract_jmeter(FIXTURES / "jmeter.jtl")
    fact = inv.facts[0]
    assert fact.measures["samples"] == 4
    assert fact.measures["errors"] == 1
    assert fact.measures["error_rate"] == 0.25
    assert fact.attrs["p99_ms"] == 310
    assert "POST /orders" in fact.attrs["labels"]


def test_gatling_global_stats() -> None:
    inv = extract_gatling(FIXTURES / "gatling-global_stats.json")
    fact = inv.facts[0]
    assert fact.measures["requests"] == 5000
    assert fact.measures["mean_ms"] == 61
    assert fact.measures["p95_ms"] == 140
    assert fact.measures["p99_ms"] == 260


def test_gatling_accepts_report_dir(tmp_path: Path) -> None:
    (tmp_path / "js").mkdir()
    (tmp_path / "js" / "global_stats.json").write_text(
        (FIXTURES / "gatling-global_stats.json").read_text()
    )
    inv = extract_gatling(tmp_path)
    assert inv.facts[0].measures["requests"] == 5000


def test_vegeta_json_report() -> None:
    inv = extract_vegeta(FIXTURES / "vegeta-report.json")
    fact = inv.facts[0]
    assert fact.measures["requests"] == 2000
    assert fact.measures["rate"] == 33.33
    assert fact.measures["success_rate"] == 0.995
    assert fact.attrs["p99_ms"] == 300.0  # nanoseconds converted to ms


def test_wrk_text_summary() -> None:
    inv = extract_wrk(FIXTURES / "wrk-summary.txt")
    fact = inv.facts[0]
    assert fact.measures["requests"] == 72000
    assert fact.measures["rps"] == 2399.2
    assert fact.measures["non_2xx"] == 15
    assert fact.attrs["p99"] == "210.00ms"


def test_hey_csv() -> None:
    inv = extract_hey(FIXTURES / "hey.csv")
    fact = inv.facts[0]
    assert fact.measures["requests"] == 3
    assert fact.attrs["max_ms"] == 120.0
    assert fact.attrs["p99_ms"] is not None


def test_pytest_benchmark_per_benchmark_facts() -> None:
    inv = extract_pytest_benchmark(FIXTURES / "pytest-benchmark.json")
    assert len(inv.facts) == 2
    names = {f.measures["name"] for f in inv.facts}
    assert names == {"test_parse", "test_render"}
    parse = next(f for f in inv.facts if f.measures["name"] == "test_parse")
    assert parse.measures["rounds"] == 100


def test_missing_report_names_blind_spot(tmp_path: Path) -> None:
    for extract in (
        extract_locust,
        extract_jmeter,
        extract_gatling,
        extract_vegeta,
        extract_wrk,
        extract_hey,
        extract_pytest_benchmark,
    ):
        inv = extract(tmp_path / "absent.out")
        assert not inv.facts
        assert any(
            d.code == "AF-TEST-REPORT-MISSING" for d in inv.diagnostics
        ), extract.__name__
