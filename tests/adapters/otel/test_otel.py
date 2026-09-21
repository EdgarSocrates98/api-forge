"""OTel ingest — perf.otel.* facts, PerformanceRun, named blind spots."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.otel.extract import extract_otel
from apiforge.adapters.otel.run import build_performance_run

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "otel"


def test_extracts_operations_with_stats() -> None:
    inventory = extract_otel(FIXTURE / "baseline.json")
    ops = {
        f.measures["operation"]: f.measures
        for f in inventory.facts
        if f.kind == "perf.otel.operation"
    }
    assert set(ops) == {"GET /orders/{id}", "POST /orders"}
    get_op = ops["GET /orders/{id}"]
    assert get_op["count"] == 5
    assert get_op["mean_ms"] == 41.0
    assert get_op["max_ms"] == 45.0
    assert get_op["p95_ms"] == 45.0


def test_run_fact_and_service_name() -> None:
    inventory = extract_otel(FIXTURE / "baseline.json")
    run = next(f for f in inventory.facts if f.kind == "perf.otel.run")
    assert run.measures["span_count"] == 11
    assert run.measures["error_spans"] == 0
    assert run.attrs["service"] == "orders-api"


def test_incomplete_span_is_named_not_dropped() -> None:
    inventory = extract_otel(FIXTURE / "baseline.json")
    codes = [d.code for d in inventory.diagnostics]
    assert "AF-OTEL-SPAN-INCOMPLETE" in codes
    diag = next(d for d in inventory.diagnostics if d.code == "AF-OTEL-SPAN-INCOMPLETE")
    assert "1 of 11" in diag.message


def test_invalid_export_is_diagnostic(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    inventory = extract_otel(bad)
    assert any(d.code == "AF-OTEL-REPORT-INVALID" for d in inventory.diagnostics)


def test_missing_resourcespans_is_diagnostic(tmp_path: Path) -> None:
    bad = tmp_path / "empty.json"
    bad.write_text("{}", encoding="utf-8")
    inventory = extract_otel(bad)
    assert any(d.code == "AF-OTEL-REPORT-INVALID" for d in inventory.diagnostics)


def test_missing_service_name_is_unresolved(tmp_path: Path) -> None:
    doc = {"resourceSpans": [{"resource": {"attributes": []},
                              "scopeSpans": [{"spans": []}]}]}
    path = tmp_path / "nosvc.json"
    path.write_text(__import__("json").dumps(doc), encoding="utf-8")
    inventory = extract_otel(path)
    assert any(d.code == "AF-OTEL-SERVICE-UNKNOWN" for d in inventory.diagnostics)
    run = build_performance_run(inventory, path.name)
    assert run.subject == "" or "AF-OTEL-SERVICE-UNKNOWN" in run.unresolved


def test_performance_run_populated() -> None:
    inventory = extract_otel(FIXTURE / "baseline.json")
    run = build_performance_run(inventory, "baseline.json")
    assert run.subject == "orders-api"
    ops = run.attributes["operations"]
    assert set(ops) == {"GET /orders/{id}", "POST /orders"}
    assert ops["POST /orders"]["mean_ms"] == 80.0
    assert run.unresolved == ("AF-OTEL-SPAN-INCOMPLETE",)


def test_extraction_deterministic() -> None:
    a = extract_otel(FIXTURE / "candidate.json")
    b = extract_otel(FIXTURE / "candidate.json")
    assert [f.fact_id for f in a.facts] == [f.fact_id for f in b.facts]
