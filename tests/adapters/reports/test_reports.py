"""Report readers: valid fixtures -> facts; missing/malformed -> diagnostics."""

import json
from pathlib import Path

import pytest

from apiforge.adapters.secreports import (
    extract_gitleaks,
    extract_semgrep,
    extract_trivy,
    extract_zap,
)
from apiforge.adapters.testreports import (
    extract_coverage,
    extract_k6,
    extract_pact,
    extract_schemathesis,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "reports"

READERS = {
    "pact": (extract_pact, "pact-orders.json", "test.pact.contract"),
    "schemathesis": (extract_schemathesis, "schemathesis.json", "test.schemathesis.run"),
    "k6": (extract_k6, "k6-summary.json", "test.k6.summary"),
    "coverage": (extract_coverage, "coverage.json", "test.coverage.py"),
    "zap": (extract_zap, "zap.json", "sec.zap.report"),
    "semgrep": (extract_semgrep, "semgrep.json", "sec.semgrep.report"),
    "trivy": (extract_trivy, "trivy.json", "sec.trivy.report"),
    "gitleaks": (extract_gitleaks, "gitleaks.json", "sec.gitleaks.report"),
}


@pytest.mark.parametrize("name", sorted(READERS))
def test_reader_emits_expected_fact(name: str) -> None:
    reader, filename, kind = READERS[name]
    inv = reader(FIXTURES / filename)
    (fact,) = inv.facts
    assert fact.kind == kind
    assert inv.diagnostics == ()


@pytest.mark.parametrize("name", sorted(READERS))
def test_missing_report_is_named_diagnostic(name: str, tmp_path: Path) -> None:
    reader, _, _ = READERS[name]
    inv = reader(tmp_path / "absent.json")
    codes = {d.code for d in inv.diagnostics}
    expected = "AF-TEST-REPORT-MISSING" if name in {"pact", "schemathesis", "k6", "coverage"} else "AF-SEC-REPORT-MISSING"
    assert codes == {expected}
    assert inv.facts == ()


def test_pact_facts() -> None:
    inv = extract_pact(FIXTURES / "pact-orders.json")
    fact = inv.facts[0]
    assert fact.measures["provider"] == "orders-api"
    assert fact.attrs["consumer"] == "storefront"
    assert fact.attrs["interactions"] == 2
    assert fact.attrs["methods"] == ("GET", "POST")


def test_schemathesis_totals() -> None:
    inv = extract_schemathesis(FIXTURES / "schemathesis.json")
    fact = inv.facts[0]
    assert fact.measures["checks_total"] == 480
    assert fact.attrs["failure"] == 3


def test_k6_metrics() -> None:
    inv = extract_k6(FIXTURES / "k6-summary.json")
    fact = inv.facts[0]
    assert fact.attrs["duration_p95_ms"] == 120.5
    assert fact.attrs["failed_rate"] == 0.002
    # RPS (requests) and TPS candidate (iterations) are distinct measures
    assert fact.measures["rps"] == 60.0
    assert fact.measures["iterations_rate"] == 20.0
    assert fact.measures["dropped_iterations"] == 0


def test_k6_dropped_iterations_fire_generator_saturation() -> None:
    from apiforge.rules.fact_judge import judge_facts

    inv = extract_k6(FIXTURES / "k6-summary.json")
    fact = inv.facts[0].model_copy(
        update={"measures": {**inv.facts[0].measures, "dropped_iterations": 40}}
    )
    findings = judge_facts([fact])
    fired = {f.rule_id for f in findings}
    assert "AF-TEST-104" in fired


def test_gitleaks_never_emits_secret() -> None:
    inv = extract_gitleaks(FIXTURES / "gitleaks.json")
    payload = json.dumps(inv.model_dump(mode="json"))
    assert "AKIA" not in payload and "sk_live" not in payload
    fact = inv.facts[0]
    assert fact.measures["leaks"] == 2
    assert fact.attrs["by_rule"] == {"aws-access-key": 1, "generic-api-key": 1}
