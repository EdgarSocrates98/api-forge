"""Report sign/verify: round-trip + every divergence part named."""

import json
from pathlib import Path

import pytest

from apiforge.report.bundle import ReportError, build_report, canonical
from apiforge.report.sign import sign_report, verify_report

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture()
def case(tmp_path: Path) -> Path:
    from apiforge.application.analyze import analyze_project

    out = tmp_path / "case"
    analyze_project(
        FIXTURES / "openapi" / "orders-v1.yaml",
        FIXTURES / "fastapi_orders",
        None,
        out,
    )
    return out


def test_build_report_bundles_case(case: Path) -> None:
    report = build_report(case, now="2026-09-21T00:00:00Z")
    assert report["report_version"] == 1
    assert report["case_id"]
    assert report["catalog_sha256"]
    assert report["policy_sha256"]
    assert report["findings"]["total"] > 0
    assert report["emitted_at"] == "2026-09-21T00:00:00Z"


def test_sign_verify_round_trip(case: Path) -> None:
    signed = sign_report(build_report(case))
    result = verify_report(signed)
    assert result["ok"] is True
    assert result["diverged"] == []


def test_unsigned_report_refuses(case: Path) -> None:
    with pytest.raises(ReportError, match="AF-REPORT-UNSIGNED"):
        verify_report(build_report(case))


def test_body_divergence_named(case: Path) -> None:
    signed = sign_report(build_report(case))
    tampered = {**signed, "case_id": "tampered"}
    result = verify_report(tampered)
    assert result["ok"] is False
    assert "body" in result["diverged"]


def test_evidence_divergence_named(case: Path, tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    receipt.write_text(canonical({"schema_version": "af-receipt/1"}))
    signed = sign_report(build_report(case, receipt_path=receipt))
    receipt.write_text(canonical({"schema_version": "af-receipt/1", "tampered": True}))
    result = verify_report(signed, receipt_path=receipt)
    assert "evidence" in result["diverged"]


def test_signature_version_divergence(case: Path) -> None:
    signed = sign_report(build_report(case))
    signed["signature"] = {**signed["signature"], "version": 99}
    result = verify_report(signed)
    assert "signature_version" in result["diverged"]


def test_cli_sign_verify_e2e(case: Path, tmp_path: Path) -> None:
    from typer.testing import CliRunner

    from apiforge.cli import app

    runner = CliRunner()
    report_path = tmp_path / "report.json"
    r = runner.invoke(
        app,
        ["report", "build", "--case", str(case), "--out", str(report_path)],
    )
    assert r.exit_code == 0
    r = runner.invoke(app, ["report", "sign", "--report", str(report_path)])
    assert r.exit_code == 0
    r = runner.invoke(app, ["report", "verify", "--report", str(report_path)])
    assert r.exit_code == 0
    assert json.loads(r.output)["ok"] is True
    # tamper → exit 4
    doc = json.loads(report_path.read_text())
    doc["case_id"] = "forged"
    report_path.write_text(canonical(doc))
    r = runner.invoke(app, ["report", "verify", "--report", str(report_path)])
    assert r.exit_code == 4
    assert "body" in json.loads(r.output)["diverged"]
