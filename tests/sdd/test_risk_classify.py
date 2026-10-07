import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.sdd.checks import check
from apiforge.sdd.risk import classify, profile_below_risk

REPO = Path(__file__).resolve().parents[2]
runner = CliRunner()


@pytest.mark.parametrize(
    ("kwargs", "risk_class", "profile"),
    [
        ({"paths": ("docs/guide.md",)}, "micro", "micro"),
        ({"description": "fix typo in README"}, "micro", "micro"),
        ({"paths": ("src/app/handlers.py",)}, "low", "quick"),
        ({"contract_verdict": "compatible"}, "low", "quick"),
        ({"paths": ("api/openapi.yaml",)}, "medium", "standard"),
        ({"paths": ("src/apiforge/contracts/routing.py",)}, "medium", "standard"),
        ({"description": "add optional field to the order schema"}, "medium", "standard"),
        ({"contract_verdict": "breaking"}, "high", "critical"),
        ({"paths": ("src/auth/tokens.py",)}, "high", "critical"),
        ({"description": "migrate payment authentication"}, "high", "critical"),
        ({"description": "rename field", "repositories": 3}, "high", "migration"),
    ],
)
def test_classify_maps_signals_to_minimum_profile(kwargs, risk_class, profile) -> None:
    result = classify(**kwargs)
    assert result.risk_class == risk_class
    assert result.sdd_profile == profile
    assert result.signals


def test_missing_signals_never_classify_below_medium() -> None:
    result = classify()
    assert result.risk_class == "medium"
    assert result.unresolved[0].startswith("AF-SDD-RISK-UNRESOLVED")


def test_profile_rank_comparison() -> None:
    assert profile_below_risk("quick", "high")
    assert not profile_below_risk("critical", "high")
    assert not profile_below_risk("migration", "high")
    assert not profile_below_risk("micro", "micro")


def _feature(tmp_path: Path) -> Path:
    source = REPO / "docs" / "sdd" / "API_FORGE_DEVIN_INTEGRATION"
    target = tmp_path / "sdd" / "API_FORGE_DEVIN_INTEGRATION"
    shutil.copytree(source, target)
    return target


def test_sdd_check_refuses_profile_below_classified_risk(tmp_path: Path) -> None:
    feature = _feature(tmp_path)
    result = runner.invoke(
        app,
        ["sdd", "classify", "--path", "src/auth/login.py", "--write", str(feature)],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["risk_class"] == "high"
    report = check(tmp_path / "sdd", feature="API_FORGE_DEVIN_INTEGRATION")
    codes = {issue.code for issue in report.refused}
    assert "AF-SDD-PROFILE-BELOW-RISK" in codes
    refusal = next(item for item in report.refused if item.code == "AF-SDD-PROFILE-BELOW-RISK")
    assert refusal.field == "profile"
    assert "critical" in (refusal.unlock or "")


def test_features_without_risk_class_are_unaffected(tmp_path: Path) -> None:
    _feature(tmp_path)
    report = check(tmp_path / "sdd", feature="API_FORGE_DEVIN_INTEGRATION")
    assert "AF-SDD-PROFILE-BELOW-RISK" not in {issue.code for issue in report.refused}


def test_classify_uses_contract_diff() -> None:
    result = runner.invoke(
        app,
        [
            "sdd",
            "classify",
            "--baseline",
            str(REPO / "tests/fixtures/openapi/orders-v1.yaml"),
            "--candidate",
            str(REPO / "tests/fixtures/openapi/orders-v2-breaking.yaml"),
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["risk_class"] == "high"
    assert "contract:breaking" in payload["signals"]
