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
    "AF-SEC-101",
    "AF-SEC-102",
    "AF-SEC-103",
    "AF-SEC-104",
    "AF-TEST-001",
    "AF-TEST-002",
    "AF-TEST-003",
    "AF-TEST-004",
    "AF-TEST-005",
    "AF-TEST-006",
    "AF-TEST-007",
    "AF-TEST-101",
    "AF-TEST-102",
    "AF-TEST-103",
    "AF-TEST-104",
    "AF-PERF-001",
    "AF-PERF-002",
    "AF-PERF-003",
    "AF-PERF-004",
    "AF-PERF-005",
    "AF-PERF-006",
    "AF-PERF-007",
    "AF-PERF-101",
    "AF-PERF-102",
    "AF-PERF-103",
    "AF-PERF-104",
    "AF-PERF-105",
    "AF-PERF-106",
    "AF-PERF-107",
    "AF-PERF-108",
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
    # data-access rules (Redis/Valkey)
    "AF-DATA-001",
    "AF-DATA-002",
    "AF-DATA-003",
    "AF-DATA-004",
    "AF-DATA-005",
    "AF-DATA-006",
    "AF-DATA-007",
    "AF-DATA-008",
    # AWS breadth: messaging + identity dump rules
    "AF-MSG-001",
    "AF-MSG-002",
    "AF-MSG-003",
    "AF-MSG-004",
    "AF-IAM-001",
    "AF-IAM-002",
    "AF-IAM-003",
    "AF-IAM-004",
    "AF-IAM-005",
    "AF-SEC-105",
    "AF-SEC-106",
    # AWS breadth batch 2: datastore, observability and edge-posture rules
    "AF-STORE-001",
    "AF-STORE-002",
    "AF-STORE-003",
    "AF-STORE-004",
    "AF-STORE-005",
    "AF-STORE-006",
    "AF-STORE-007",
    "AF-OBS-001",
    "AF-OBS-002",
    "AF-OBS-003",
    "AF-OBS-004",
    "AF-OBS-005",
    "AF-SEC-107",
    "AF-SEC-108",
    "AF-SEC-109",
    "AF-SEC-110",
    "AF-SEC-111",
    "AF-SEC-112",
    "AF-SEC-113",
    "AF-SEC-114",
    "AF-SEC-115",
    "AF-SEC-116",
    "AF-GW-008",
    # Data-access rules for MongoDB/DynamoDB/Neptune call sites
    "AF-DATA-009",
    "AF-DATA-010",
    "AF-DATA-011",
    "AF-DATA-012",
    "AF-DATA-013",
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
        "DATA",
        "GATEWAY",
        "IDENTITY",
        "MESSAGING",
        "OBSERVE",
        "PERF",
        "REST",
        "SECURITY",
        "STORAGE",
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
        "DATA": "AF-DATA-",
        "MESSAGING": "AF-MSG-",
        "IDENTITY": "AF-IAM-",
        "OBSERVE": "AF-OBS-",
        "STORAGE": "AF-STORE-",
    }
    for rule_id, meta in load_catalog().items():
        assert rule_id.startswith(expected[meta.area]), rule_id
