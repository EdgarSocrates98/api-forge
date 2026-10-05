"""§28 lab scenario catalog — declared coverage, honest gaps."""

from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.labs.catalog import SCENARIO_KINDS, load_lab_report

REPO = Path(__file__).resolve().parents[2]
CATALOG = REPO / "labs" / "scenarios.yaml"


def test_every_par28_kind_is_declared() -> None:
    report = load_lab_report(CATALOG, repo_root=REPO)
    declared = {scenario.kind for scenario in report.scenarios}
    for kind in SCENARIO_KINDS:
        assert kind in declared, f"§28 scenario {kind!r} missing from catalog"


def test_coverage_pointers_are_real() -> None:
    report = load_lab_report(CATALOG, repo_root=REPO)
    assert report.totals["scenarios"] == len(SCENARIO_KINDS)
    assert report.totals["covered"] == len(SCENARIO_KINDS)
    assert report.totals["declared_gap"] == 0
    assert not any("pointer" in u for u in report.unresolved)


def test_undeclared_cell_refuses(tmp_path: Path) -> None:
    catalog = tmp_path / "scenarios.yaml"
    catalog.write_text("scenarios:\n  - kind: timeout\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-LAB-CELL-UNDECLARED"):
        load_lab_report(catalog)


def test_conflicting_cell_refuses(tmp_path: Path) -> None:
    catalog = tmp_path / "scenarios.yaml"
    catalog.write_text(
        "scenarios:\n  - kind: timeout\n    fixture: x\n    gap: y\n",
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="AF-LAB-CELL-CONFLICT"):
        load_lab_report(catalog)


def test_missing_catalog_refuses(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-LAB-CATALOG-MISSING"):
        load_lab_report(tmp_path / "absent.yaml")
