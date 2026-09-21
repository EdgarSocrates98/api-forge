"""E2E: `apiforge context funnel` measures stage bytes of a persisted case."""

import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.application.funnel import measure_funnel
from apiforge.cli import app

runner = CliRunner()
FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_funnel_reports_measured_stages(tmp_path: Path) -> None:
    case = tmp_path / "case"
    runner.invoke(
        app,
        [
            "analyze",
            "--contract",
            str(FIXTURES / "openapi" / "orders-v1.yaml"),
            "--project",
            str(FIXTURES / "fastapi_orders"),
            "--out-dir",
            str(case),
        ],
    )
    result = runner.invoke(app, ["context", "funnel", "--case", str(case)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    stages = {s["stage"]: s["bytes"] for s in data["stages"]}
    assert set(stages) == {"api_ir", "facts", "findings", "findings_summary"}
    assert stages["facts"] > 0
    assert stages["findings_summary"] <= stages["findings"]
    assert "findings_to_findings_summary" in data["reduction"]
    assert data["diagnostics"] == []


def test_funnel_missing_case_refuses(tmp_path: Path) -> None:
    result = runner.invoke(app, ["context", "funnel", "--case", str(tmp_path / "none")])
    assert result.exit_code == 2
    assert "AF-INPUT-NOT-FOUND" in result.output


def test_funnel_missing_artifact_is_diagnostic(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "findings.json").write_text("[]")
    data = measure_funnel(case)
    codes = {d["code"] for d in data["diagnostics"]}
    assert codes == {"AF-FUNNEL-ARTIFACT-MISSING"}
    stages = {s["stage"] for s in data["stages"]}
    assert stages == {"findings", "findings_summary"}
