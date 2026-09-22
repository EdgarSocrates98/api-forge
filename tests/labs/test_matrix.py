"""Lab matrix — declared technology x case coverage (AT-007).

Every cell either points at a real fixture (and an eval that resolves in
the knowledge packs) or names its gap. A cell with neither is a coverage
failure — declared gaps are honest, missing pointers are not.
"""

import json
from pathlib import Path

MATRIX = Path(__file__).resolve().parent / "matrix.yaml"
REPO = Path(__file__).resolve().parents[2]

TECHNOLOGIES = {
    "fastapi",
    "spring-boot",
    "go-chi",
    "redis",
    "mongodb",
    "documentdb",
    "dynamodb",
    "neptune",
    "terraform",
    "sam",
    "api-gateway",
    "lambda",
}
CASES = {
    "correct_case",
    "route_absent",
    "schema_incompatible",
    "auth_absent",
    "pagination_absent",
    "wrong_index",
    "hot_partition",
    "unbounded_query",
    "timeout_absent",
    "unsafe_retry",
    "contract_test_absent",
    "false_positive_finding",
    "insufficient_information",
    "breaking_change",
    "incomplete_telemetry",
    "inconclusive_benchmark",
}


def _cells() -> list[dict[str, str]]:
    import yaml

    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    return list(data["cells"])


def _eval_ids() -> set[str]:
    from apiforge.knowledge.loader import load_packs

    return {
        f"{pack.domain}:{e['id']}"
        for pack in load_packs(REPO / "knowledge").values()
        for e in pack.evals
    }


def test_matrix_shape_is_the_spec_grid() -> None:
    cells = _cells()
    assert len(cells) == len(TECHNOLOGIES) * len(CASES)
    assert {c["technology"] for c in cells} == TECHNOLOGIES
    assert {c["case"] for c in cells} == CASES
    seen = {(c["technology"], c["case"]) for c in cells}
    assert len(seen) == len(cells)  # no duplicate cells


def test_every_cell_resolves_or_names_gap() -> None:
    """AT-007: a cell lacking both fixture and gap fails, named."""
    eval_ids = _eval_ids()
    bad: list[str] = []
    for cell in _cells():
        label = f"{cell.get('technology')}/{cell.get('case')}"
        fixture = cell.get("fixture")
        gap = cell.get("gap")
        if fixture:
            if not (REPO / fixture).exists():
                bad.append(f"{label}: fixture {fixture} missing")
            eval_ref = cell.get("eval")
            if eval_ref and eval_ref not in eval_ids:
                bad.append(f"{label}: eval {eval_ref} not in packs")
        elif not gap:
            bad.append(f"{label}: no fixture and no gap")
    assert not bad, json.dumps(bad, indent=2)


def test_gaps_are_named_not_empty() -> None:
    for cell in _cells():
        if "gap" in cell:
            assert cell["gap"].strip(), cell


def test_every_technology_covers_all_cases() -> None:
    from collections import Counter

    per_tech = Counter(c["technology"] for c in _cells())
    assert set(per_tech.values()) == {len(CASES)}
