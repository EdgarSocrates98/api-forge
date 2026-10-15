#!/usr/bin/env python3
"""Forge Lab emitter — loads the §28 lab scenario catalog (labs/catalog.py),
verifies honest coverage states and emits forge/BenchmarkResult/v1.

Runs under api-forge's own interpreter (uv-managed .venv): the catalog
needs pydantic, unavailable in the coordinator's stdlib-only venv.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FORGE = "api-forge"
SUITE = "api-forge-lab"


import re as _re

def _slug(s: object) -> str:
    return _re.sub(r"[^a-z0-9-]+", "-", str(s).lower()).strip("-") or "scenario"


def m(state: str, value: object = None, unit: str = "") -> dict:
    return {"state": state, "unit": unit, "value": value}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkout", required=True)
    ap.add_argument("--mode", default="A", choices=["A", "B", "C"])
    ap.add_argument("--result-out", required=True)
    a = ap.parse_args()
    checkout = Path(a.checkout).resolve()
    sys.path.insert(0, str(checkout / "src"))

    from apiforge.labs.catalog import load_lab_report

    started = time.monotonic()
    report = load_lab_report(checkout / "labs" / "scenarios.yaml", repo_root=checkout)
    elapsed = int((time.monotonic() - started) * 1000)
    data = report if isinstance(report, dict) else getattr(report, "to_dict", lambda: vars(report))()

    scenarios = [
        s.model_dump() if hasattr(s, "model_dump") else s
        for s in data.get("scenarios", [])
    ]
    covered = sum(1 for s in scenarios if s.get("state") == "covered")
    gaps = sum(1 for s in scenarios if s.get("state") == "declared-gap")
    total = len(scenarios)

    results = []
    for s in scenarios:
        state = s.get("state", "unknown")
        results.append(
            {
                "scenario_id": _slug(f"catalog-{s.get('kind', 'unknown')}"),
                "verdict": "pass" if state == "covered" else "skipped",
                "duration_ms": elapsed,
                "detail": str(s.get("gap") or s.get("note") or ""),
                "evidence_ref": str(s.get("fixture") or s.get("proof") or s.get("eval") or "")
                or "",
                "judge": None,
                "metrics": {
                    "success": m("measured", 1.0 if state == "covered" else 0.0, "ratio"),
                    "evidence_coverage": m("measured", covered / total if total else None, "ratio")
                    if total
                    else m("not_available"),
                    "cost_usd": m("not_applicable"),
                    "tokens": m("not_applicable"),
                },
            }
        )
    # Aggregate coverage scenario — the §9.5 evidence_coverage metric over
    # the declared catalog; a cell with no coverage and no declared gap is
    # a catalog load error (loader raises before we get here).
    results.append(
        {
            "scenario_id": "catalog-coverage-aggregate",
            "verdict": "pass" if covered + gaps == total and total else "fail",
            "duration_ms": elapsed,
            "detail": f"{covered} covered, {gaps} declared-gap of {total}",
            "evidence_ref": "labs/scenarios.yaml",
            "judge": None,
            "metrics": {
                "success": m("measured", 1.0 if covered + gaps == total else 0.0, "ratio"),
                "evidence_coverage": m("measured", covered / total if total else None, "ratio")
                if total
                else m("not_available"),
                "components_matched": m("measured", covered),
                "components_total": m("measured", total),
                "cost_usd": m("not_applicable"),
            },
        }
    )

    receipt = {
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "external": False,
        "suite": SUITE,
        "forge": FORGE,
        "mode": a.mode,
        "notes": ["catalog=labs/scenarios.yaml", "coverage states are declared, not executed"],
        "producer": {"id": FORGE, "version": "lab-script"},
        "results": results,
    }
    out = Path(a.result_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
