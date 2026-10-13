import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app

runner = CliRunner()


def test_next_step_routes_via_cli(tmp_path: Path) -> None:
    findings = [
        {
            "finding_id": "finding:1",
            "rule_id": "AF-CONTRACT-001",
            "title": "t",
            "severity": "high",
            "status": "confirmed",
            "detail": "d",
            "evidence": ["fact:x"],
        }
    ]
    path = tmp_path / "findings.json"
    path.write_text(json.dumps(findings), encoding="utf-8")
    result = runner.invoke(app, ["next-step", "--findings", str(path), "--phase", "verify"])
    assert result.exit_code == 0
    step = json.loads(result.stdout)
    assert step["recommended_agent"] == "api-governance-reviewer"
    assert step["dominant_area"] == "CONTRACT"


def test_next_step_accepts_official_findings_envelope(tmp_path: Path) -> None:
    payload = {
        "findings": [
            {
                "finding_id": "finding:envelope",
                "rule_id": "AF-CONTRACT-001",
                "title": "t",
                "severity": "high",
                "status": "confirmed",
                "detail": "d",
                "evidence": ["fact:x"],
            }
        ]
    }
    path = tmp_path / "findings.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = runner.invoke(app, ["next-step", "--findings", str(path), "--phase", "verify"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["recommended_agent"] == "api-governance-reviewer"


def test_next_step_no_route_exits_3(tmp_path: Path) -> None:
    findings = [
        {
            "finding_id": "finding:1",
            "rule_id": "AF-CONTRACT-001",
            "title": "t",
            "severity": "high",
            "status": "confirmed",
            "detail": "d",
            "evidence": ["fact:x"],
        }
    ]
    path = tmp_path / "findings.json"
    path.write_text(json.dumps(findings), encoding="utf-8")
    result = runner.invoke(app, ["next-step", "--findings", str(path), "--phase", "ship"])
    assert result.exit_code != 0
    assert "AF-ROUTING-NO-ROUTE" in result.stderr or "AF-ROUTING-NO-ROUTE" in result.stdout
