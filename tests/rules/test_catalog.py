from pathlib import Path

import pytest

from apiforge.rules.catalog import (
    CatalogError,
    load_areas,
    load_catalog,
    load_catalog_text,
)

_DOC = """\
catalog_version: 1
schema_version: 1
area: REST
retrieved: 2026-09-21
rules:
  - id: AF-REST-001
    title: t
    severity: low
    rationale: r
    remediation: m
"""


def test_catalog_merges_all_area_files() -> None:
    catalog = load_catalog()
    assert catalog["AF-CONTRACT-001"].area == "CONTRACT"
    assert catalog["AF-CONTRACT-001"].title
    assert "REST" in load_areas()


def test_load_areas_is_sorted_and_unique() -> None:
    areas = load_areas()
    assert areas == tuple(sorted(set(areas)))
    assert "CONTRACT" in areas


def test_expected_gain_is_refused_by_schema() -> None:
    doc = _DOC.replace("severity: low", "severity: low\n    expected_gain: 2x")
    with pytest.raises(CatalogError, match="AF-CATALOG-SCHEMA"):
        load_catalog_text(doc)


def test_unknown_rule_key_is_refused() -> None:
    doc = _DOC.replace("severity: low", "severity: low\n    surprise: x")
    with pytest.raises(CatalogError, match="AF-CATALOG-SCHEMA"):
        load_catalog_text(doc)


def test_missing_file_area_is_refused() -> None:
    doc = _DOC.replace("area: REST\n", "")
    with pytest.raises(CatalogError, match="AF-CATALOG-AREA-MISSING"):
        load_catalog_text(doc)


def test_duplicate_rule_id_across_files_is_refused(tmp_path: Path) -> None:
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    a.write_text(_DOC, encoding="utf-8")
    b.write_text(_DOC.replace("area: REST", "area: PERF"), encoding="utf-8")
    with pytest.raises(CatalogError, match="AF-CATALOG-DUPLICATE-RULE"):
        load_catalog(tmp_path)


def test_runtime_scope_round_trips() -> None:
    doc = _DOC.replace("severity: low", "severity: low\n    runtime_scope: spring-boot >= 3")
    catalog = load_catalog_text(doc)
    assert catalog["AF-REST-001"].runtime_scope == "spring-boot >= 3"
