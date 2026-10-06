"""judge_facts applies catalog `check` rules to facts — evidence is the fact_id."""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.adapters.secreports import extract_gitleaks, extract_trivy
from apiforge.adapters.testreports import extract_coverage, extract_k6
from apiforge.rules.catalog import load_catalog
from apiforge.rules.fact_judge import judge_facts


def _write(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_k6_failed_rate_fires(tmp_path: Path) -> None:
    report = _write(
        tmp_path / "k6.json",
        {"metrics": {"http_req_failed": {"rate": 0.12}, "vus_max": {"value": 50}}},
    )
    findings = judge_facts(extract_k6(report).facts)
    fired = [f for f in findings if f.rule_id == "AF-TEST-101"]
    assert len(fired) == 1
    assert fired[0].severity == "high"
    assert fired[0].evidence  # cites the fact_id


def test_k6_clean_run_stays_quiet(tmp_path: Path) -> None:
    report = _write(
        tmp_path / "k6.json",
        {"metrics": {"http_req_failed": {"rate": 0.01}, "vus_max": {"value": 50}}},
    )
    assert judge_facts(extract_k6(report).facts) == ()


def test_coverage_below_floor_fires(tmp_path: Path) -> None:
    report = _write(tmp_path / "cov.json", {"totals": {"percent_covered": 61.5}, "files": {}})
    assert {f.rule_id for f in judge_facts(extract_coverage(report).facts)} == {"AF-TEST-103"}


def test_gitleaks_and_trivy_fire(tmp_path: Path) -> None:
    leaks = _write(tmp_path / "leaks.json", [{"RuleID": "aws-key", "File": "a.py"}])
    trivy = _write(
        tmp_path / "trivy.json",
        {
            "Results": [
                {
                    "Target": "app",
                    "Vulnerabilities": [{"Severity": "CRITICAL", "VulnerabilityID": "V"}],
                }
            ]
        },
    )
    rules = {
        f.rule_id
        for f in judge_facts((*extract_gitleaks(leaks).facts, *extract_trivy(trivy).facts))
    }
    assert rules == {"AF-SEC-101", "AF-SEC-102"}


def test_clean_reports_produce_no_findings(tmp_path: Path) -> None:
    trivy = _write(
        tmp_path / "trivy.json",
        {"Results": [{"Target": "app", "Vulnerabilities": [{"Severity": "LOW"}]}]},
    )
    assert judge_facts(extract_trivy(trivy).facts) == ()


def test_check_rules_are_catalog_data() -> None:
    """Every check rule loads; thresholds live in the catalog, not in code."""
    checks = {rid: m.check for rid, m in load_catalog().items() if m.check}
    assert {
        "AF-TEST-101",
        "AF-TEST-102",
        "AF-TEST-103",
        "AF-SEC-101",
        "AF-SEC-102",
        "AF-SEC-103",
        "AF-SEC-104",
    } <= set(checks)
    assert checks["AF-TEST-101"].op == "gt"
