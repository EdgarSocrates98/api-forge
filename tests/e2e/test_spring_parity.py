from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.application.analyze import AnalysisError, analyze_project
from apiforge.cli import app

runner = CliRunner()
CONTRACT = Path("tests/fixtures/openapi/orders-v1.yaml")


def _verdicts(result) -> list[tuple[str, str, str]]:
    return sorted((f.rule_id, f.severity.value, f.status.value) for f in result.findings)


def test_spring_and_fastapi_findings_parity(tmp_path: Path) -> None:
    fastapi = analyze_project(
        CONTRACT,
        Path("tests/fixtures/fastapi_orders"),
        None,
        tmp_path / "fastapi",
        framework="fastapi",
    )
    spring = analyze_project(
        CONTRACT,
        Path("tests/labs/orders-spring"),
        None,
        tmp_path / "spring",
        framework="spring",
    )
    assert _verdicts(spring) == _verdicts(fastapi)
    assert any(f.rule_id == "AF-CODE-001" for f in spring.findings)
    assert any(f.status.value == "unresolved" for f in spring.findings)


def test_go_and_fastapi_findings_parity(tmp_path: Path) -> None:
    fastapi = analyze_project(
        CONTRACT,
        Path("tests/fixtures/fastapi_orders"),
        None,
        tmp_path / "fastapi",
        framework="fastapi",
    )
    go = analyze_project(
        CONTRACT,
        Path("tests/labs/orders-go"),
        None,
        tmp_path / "go",
        framework="go",
    )
    assert _verdicts(go) == _verdicts(fastapi)
    assert any(f.rule_id == "AF-CODE-001" for f in go.findings)
    assert any(f.status.value == "unresolved" for f in go.findings)


def test_auto_detects_go_by_go_files(tmp_path: Path) -> None:
    result = analyze_project(
        CONTRACT,
        Path("tests/labs/orders-go"),
        None,
        tmp_path / "auto",
        framework="auto",
    )
    assert result.findings


def test_auto_detects_spring_by_java_files(tmp_path: Path) -> None:
    result = analyze_project(
        CONTRACT,
        Path("tests/labs/orders-spring"),
        None,
        tmp_path / "auto",
        framework="auto",
    )
    assert result.findings


def test_unknown_framework_is_named(tmp_path: Path) -> None:
    empty = tmp_path / "nothing"
    empty.mkdir()
    with pytest.raises(AnalysisError, match="AF-INPUT-FRAMEWORK-UNKNOWN"):
        analyze_project(CONTRACT, empty, None, tmp_path / "out", framework="auto")


def test_cli_framework_option(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "analyze",
            "--contract",
            str(CONTRACT),
            "--project",
            "tests/labs/orders-spring",
            "--framework",
            "spring",
            "--out-dir",
            str(tmp_path / "cli"),
        ],
    )
    assert result.exit_code == 0
