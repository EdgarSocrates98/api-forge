"""Multi-agent ROI (§79): did each extra agent change anything?

For every stored run, the primary capability's artifact is the reference.
Each other capability's artifact is compared with it: facts and unresolved
items it added, and whether its recommendation differs (``outcome_changed``).
Aggregated per capability across runs, this is the evidence a router needs
to stop calling an agent that rarely changes the outcome.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.contracts.economy_evals import RoleROI


def _artifacts(run_dir: Path) -> list[dict[str, Any]]:
    folder = run_dir / "artifacts"
    if not folder.is_dir():
        return []
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(folder.glob("*.json"))]


def role_roi(root: Path) -> dict[str, Any]:
    tasks = Path(root) / ".apiforge" / "tasks"
    totals: dict[str, dict[str, int]] = {}
    runs_seen = 0
    for run_dir in sorted(tasks.glob("*/runs/*")) if tasks.is_dir() else []:
        plan_path = run_dir / "routing-plan.json"
        if not run_dir.is_dir() or not plan_path.is_file():
            continue
        primary = json.loads(plan_path.read_text(encoding="utf-8")).get("primary")
        artifacts = _artifacts(run_dir)
        reference = next((item for item in artifacts if item.get("capability") == primary), None)
        if reference is None:
            continue
        runs_seen += 1
        ref_facts = set(reference.get("evidence") or ())
        ref_unresolved = set(reference.get("unresolved") or ())
        ref_outcome = str((reference.get("payload") or {}).get("recommendation", ""))
        for item in artifacts:
            name = str(item.get("capability"))
            if name == primary:
                continue
            row = totals.setdefault(
                name,
                {"runs": 0, "calls": 0, "facts_added": 0, "unresolved_added": 0, "changed": 0},
            )
            row["runs"] += 1
            row["calls"] += 1
            row["facts_added"] += len(set(item.get("evidence") or ()) - ref_facts)
            row["unresolved_added"] += len(set(item.get("unresolved") or ()) - ref_unresolved)
            outcome = str((item.get("payload") or {}).get("recommendation", ""))
            row["changed"] += int(outcome != ref_outcome)
    rows = [
        RoleROI(
            capability=name,
            runs=row["runs"],
            calls=row["calls"],
            facts_added=row["facts_added"],
            unresolved_added=row["unresolved_added"],
            outcome_changed=row["changed"],
            outcome_changed_rate=round(row["changed"] / row["runs"], 4) if row["runs"] else 0.0,
        )
        for name, row in sorted(totals.items())
    ]
    return {
        "schema": "apiforge/role-roi/v1",
        "runs": runs_seen,
        "roles": [row.model_dump(mode="json") for row in rows],
        "note": "outcome_changed compares recommendations with the primary artifact; "
        "facts are compared by id, never by prose",
    }


__all__ = ["role_roi"]
