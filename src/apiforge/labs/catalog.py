"""§28 lab scenario catalog — declared cells, honest coverage.

The catalog is data: each cell names a fixture, a pack eval, a test proof
or a declared gap. A cell with no pointer is a coverage failure — gaps
must be declared, never implied.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.lab import LabReport, LabScenario

SCENARIO_KINDS = (
    "breaking change",
    "schema evolution",
    "backward compatibility",
    "latency regression",
    "auth migration",
    "rate limit",
    "retry storm",
    "timeout",
    "circuit breaker",
    "event contract",
    "idempotency",
    "pagination",
    "version migration",
)


def load_lab_report(catalog_path: Path, *, repo_root: Path | None = None) -> LabReport:
    """Project the declared catalog into a LabReport.

    ``repo_root`` is used only to verify that fixture/proof pointers are
    real paths; eval ids are declared strings and stay unresolved-checked.
    """
    if not catalog_path.is_file():
        raise ContractError("AF-LAB-CATALOG-MISSING", f"lab catalog {catalog_path} not found")
    try:
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ContractError("AF-LAB-CATALOG-INVALID", f"{catalog_path}: {exc}") from exc
    cells = raw.get("scenarios") or []
    scenarios: list[LabScenario] = []
    unresolved: list[str] = []
    for index, cell in enumerate(cells):
        if not isinstance(cell, dict) or not cell.get("kind"):
            raise ContractError("AF-LAB-CELL-INVALID", f"scenarios[{index}] lacks a declared kind")
        kind = str(cell["kind"])
        fixture = cell.get("fixture")
        eval_id = cell.get("eval")
        proof = cell.get("proof")
        gap = cell.get("gap")
        covered = bool(fixture or eval_id or proof)
        if covered and gap:
            raise ContractError(
                "AF-LAB-CELL-CONFLICT",
                f"scenarios[{index}] {kind!r} declares both coverage and a gap",
            )
        if not covered and not gap:
            raise ContractError(
                "AF-LAB-CELL-UNDECLARED",
                f"scenarios[{index}] {kind!r} has no coverage pointer and no declared gap",
            )
        if repo_root is not None:
            for field_name, pointer in (("fixture", fixture), ("proof", proof)):
                if pointer and not (repo_root / str(pointer)).exists():
                    unresolved.append(f"{kind}: {field_name} pointer {pointer} not found")
        scenarios.append(
            LabScenario(
                kind=kind,
                state="covered" if covered else "declared-gap",
                fixture=str(fixture) if fixture else None,
                eval_id=str(eval_id) if eval_id else None,
                proof=str(proof) if proof else None,
                note=str(cell.get("note")) if cell.get("note") else None,
                gap=str(gap) if gap else None,
            )
        )
    declared = {scenario.kind for scenario in scenarios}
    for kind in SCENARIO_KINDS:
        if kind not in declared:
            unresolved.append(f"§28 scenario {kind!r} absent from the catalog")
    totals = {
        "scenarios": len(scenarios),
        "covered": sum(1 for s in scenarios if s.state == "covered"),
        "declared_gap": sum(1 for s in scenarios if s.state == "declared-gap"),
    }
    return LabReport(scenarios=tuple(scenarios), totals=totals, unresolved=tuple(unresolved))
