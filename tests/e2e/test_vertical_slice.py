import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app

runner = CliRunner()

CONTRACT = "tests/fixtures/openapi/orders-v1.yaml"
BASELINE = "tests/fixtures/openapi/orders-v1.yaml"
CANDIDATE = "tests/fixtures/openapi/orders-v2-breaking.yaml"
PROJECT = "tests/fixtures/fastapi_orders"


def test_analyze_command_is_reproducible(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    args = ["analyze", "--contract", CONTRACT, "--project", PROJECT]
    assert runner.invoke(app, [*args, "--out-dir", str(first)]).exit_code == 0
    assert runner.invoke(app, [*args, "--out-dir", str(second)]).exit_code == 0
    for name in ("api-ir.json", "facts.json", "findings.json", "case.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_invalid_input_returns_usage_exit_code(tmp_path: Path) -> None:
    result = runner.invoke(app, ["analyze", "--contract", "missing.yaml", "--project", "."])
    assert result.exit_code == 2
    assert "AF-INPUT-NOT-FOUND" in result.stderr


def test_analyze_prints_summary_and_writes_case(tmp_path: Path) -> None:
    out = tmp_path / "case"
    result = runner.invoke(
        app, ["analyze", "--contract", CONTRACT, "--project", PROJECT, "--out-dir", str(out)]
    )
    assert result.exit_code == 0
    summary = json.loads(result.stdout)
    assert summary["operations"] > 0
    assert (out / "case.json").exists()


def test_analyze_with_baseline_persists_changes(tmp_path: Path) -> None:
    out = tmp_path / "chg"
    result = runner.invoke(
        app,
        [
            "analyze",
            "--contract",
            CANDIDATE,
            "--project",
            PROJECT,
            "--baseline",
            BASELINE,
            "--out-dir",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert (out / "changes.json").exists()


def test_model_build_prints_api_ir() -> None:
    result = runner.invoke(app, ["model", "build", "--contract", CONTRACT, "--project", PROJECT])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["schema_version"] == "1"
    assert len(data["operations"]) > 0


def test_diff_contract_prints_changes() -> None:
    result = runner.invoke(
        app, ["diff", "contract", "--baseline", BASELINE, "--candidate", CANDIDATE]
    )
    assert result.exit_code == 0
    changes = json.loads(result.stdout)
    assert any(c["code"] == "AF-BREAKING-OPERATION-REMOVED" for c in changes)


def test_discover_lists_routes() -> None:
    result = runner.invoke(app, ["discover", "--project", PROJECT])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data["routes"]) > 0


def test_judge_lists_findings() -> None:
    result = runner.invoke(app, ["judge", "--contract", CONTRACT, "--project", PROJECT])
    assert result.exit_code == 0
    findings = json.loads(result.stdout)
    assert all("rule_id" in f for f in findings)


def test_judge_facts_mode(tmp_path: Path) -> None:
    from apiforge.adapters.secreports import extract_gitleaks

    report = tmp_path / "leaks.json"
    report.write_text(
        json.dumps([{"RuleID": "aws-key", "File": "a.py", "Secret": "AKIA-SECRET-VALUE-999"}]),
        encoding="utf-8",
    )
    inv = extract_gitleaks(report)
    facts_file = tmp_path / "facts.json"
    facts_file.write_text(
        json.dumps({"facts": [f.model_dump(mode="json") for f in inv.facts]}),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["judge", "--facts", str(facts_file)])
    assert result.exit_code == 0, result.output
    findings = json.loads(result.output)
    assert {f["rule_id"] for f in findings} == {"AF-SEC-101"}
    assert "AKIA-SECRET-VALUE-999" not in result.output


def test_judge_facts_ambiguous_input(tmp_path: Path) -> None:
    f = tmp_path / "f.json"
    f.write_text("[]", encoding="utf-8")
    result = runner.invoke(
        app,
        ["judge", "--facts", str(f), "--contract", CONTRACT, "--project", PROJECT],
    )
    assert result.exit_code != 0
    assert "AF-JUDGE-INPUT-AMBIGUOUS" in result.output
