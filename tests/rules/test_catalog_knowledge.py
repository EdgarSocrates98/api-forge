"""Lock the knowledge-catalog surface: every rule id exists, is well-formed."""

from apiforge.rules.catalog import load_areas, load_catalog

EXPECTED_RULES = {
    "AF-REST-001",
    "AF-REST-002",
    "AF-REST-003",
    "AF-REST-004",
    "AF-REST-005",
    "AF-REST-006",
    "AF-REST-007",
    "AF-REST-008",
    "AF-SEC-001",
    "AF-SEC-002",
    "AF-SEC-003",
    "AF-SEC-004",
    "AF-SEC-005",
    "AF-SEC-006",
    "AF-SEC-007",
    "AF-SEC-008",
    "AF-TEST-001",
    "AF-TEST-002",
    "AF-TEST-003",
    "AF-TEST-004",
    "AF-TEST-005",
    "AF-TEST-006",
    "AF-TEST-007",
    "AF-PERF-001",
    "AF-PERF-002",
    "AF-PERF-003",
    "AF-PERF-004",
    "AF-PERF-005",
    "AF-PERF-006",
    "AF-PERF-007",
    "AF-BREAK-001",
    "AF-BREAK-002",
    "AF-BREAK-003",
    "AF-BREAK-004",
    "AF-BREAK-005",
    "AF-BREAK-006",
    "AF-BREAK-007",
    "AF-GW-001",
    "AF-GW-002",
    "AF-GW-003",
    "AF-GW-004",
    "AF-GW-005",
    "AF-GW-006",
    "AF-GW-007",
    # plan-1 executable rules
    "AF-CONTRACT-001",
    "AF-CODE-001",
    "AF-CODE-002",
    "AF-CODE-003",
}


def test_catalog_surface_is_exact() -> None:
    assert set(load_catalog()) == EXPECTED_RULES


def test_every_rule_is_actionable() -> None:
    for rule_id, meta in load_catalog().items():
        assert meta.title and meta.rationale and meta.remediation, rule_id
        assert meta.reference, f"{rule_id} lacks a traceable source"


def test_areas_cover_the_specialist_team() -> None:
    assert set(load_areas()) == {
        "BREAKING",
        "CONTRACT",
        "GATEWAY",
        "PERF",
        "REST",
        "SECURITY",
        "TESTING",
    }


def test_id_prefix_matches_area() -> None:
    expected = {
        "REST": "AF-REST-",
        "SECURITY": "AF-SEC-",
        "TESTING": "AF-TEST-",
        "PERF": "AF-PERF-",
        "BREAKING": "AF-BREAK-",
        "GATEWAY": "AF-GW-",
        "CONTRACT": "AF-",
    }
    for rule_id, meta in load_catalog().items():
        assert rule_id.startswith(expected[meta.area]), rule_id
