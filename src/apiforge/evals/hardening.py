"""Economy hardening eval: trust boundary and budget/accounting invariants.

Deterministic, offline cases that pin the review's P1/P2 fixes:

- ``path``: a candidate source path must be allowed or refused by the
  resolver (``..``, absolute, UNC, drive, undeclared repository);
- ``budget``: a role mix must fit ``context_bytes`` through class pools;
- ``tokens``: measured/unmeasured ledger rows give the declared coverage;
- ``phase``: phase usage gives the declared ``budget_status``;
- ``delta``: an unmapped path is ``degraded`` only when it is runtime code.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    rows = [
        yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [str(row.get("id")) for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"economy-hardening corpus {corpus} empty or duplicated"
        )
    return rows


def _path(case: dict[str, Any], work: Path) -> dict[str, Any]:
    from apiforge.security.source_paths import (
        AllowedRoots,
        SourcePathError,
        resolve_allowed_source,
    )

    project = work / "project"
    (project / "src").mkdir(parents=True, exist_ok=True)
    (project / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for name in ("declared", "undeclared"):
        (work / name).mkdir(exist_ok=True)
        (work / name / "api.py").write_text("y = 2\n", encoding="utf-8")
    (project / ".apiforge").mkdir(exist_ok=True)
    (project / ".apiforge" / "workspace.yaml").write_text(
        f"repositories:\n  - root: {(work / 'declared').as_posix()}\n", encoding="utf-8"
    )
    candidate = str(case["candidate"]).replace("{work}", work.as_posix())
    try:
        resolve_allowed_source(candidate, AllowedRoots.for_project(project), base=project)
        outcome = "allow"
    except SourcePathError:
        outcome = "refuse"
    return {"outcome": outcome, "passed": outcome == case["expect"]}


def _budget(case: dict[str, Any], work: Path) -> dict[str, Any]:
    from apiforge.runtime.role_context import load_role_policy

    policy = load_role_policy()
    context_bytes = int(case["context_bytes"])
    members: dict[str, int] = {}
    for kind in case["roles"]:
        cls = str(policy["roles"][kind])
        members[cls] = members.get(cls, 0) + 1
    total = 0
    for cls, count in members.items():
        pool = int(float(policy["classes"][cls].get("share", 0)) * context_bytes)
        total += (pool // count) * count + pool % count
    return {"budget_total": total, "passed": total <= context_bytes}


def _tokens(case: dict[str, Any], work: Path) -> dict[str, Any]:
    from apiforge.contracts.economy import CostVector, RunLedgerEntry
    from apiforge.economy import run_ledger

    for tokens in case["rows"]:
        run_ledger.append(
            work,
            RunLedgerEntry(
                run_id="eval",
                verb="runtime role:specialist",
                source="envelope",
                cost=CostVector(context_bytes=1, observed_tokens=tokens),
            ),
        )
    coverage = run_ledger.stats(work)["token_coverage"]
    return {"coverage": coverage["status"], "passed": coverage["status"] == case["expect"]}


def _phase(case: dict[str, Any], work: Path) -> dict[str, Any]:
    from apiforge.economy.phase_budget import plan_phase_budgets

    usage = {str(key): dict(value) for key, value in dict(case["usage"]).items()}
    plan = plan_phase_budgets(str(case["profile"]), usage=usage)
    return {"budget_status": plan.budget_status, "passed": plan.budget_status == case["expect"]}


def _delta(case: dict[str, Any], work: Path) -> dict[str, Any]:
    from apiforge.context.delta import _runtime_path

    degraded = _runtime_path(str(case["path"]))
    return {"degraded": degraded, "passed": degraded is bool(case["expect_degraded"])}


_KINDS = {"path": _path, "budget": _budget, "tokens": _tokens, "phase": _phase, "delta": _delta}


def run_hardening(corpus: Path) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-hardening-") as tmp:
        for index, case in enumerate(load_cases(Path(corpus))):
            kind = str(case.get("kind"))
            if kind not in _KINDS:
                raise ContractError("AF-EVALS-INVALID", f"unknown case kind {kind!r}")
            work = Path(tmp) / str(index)
            work.mkdir()
            rows.append({"case_id": case["id"], "kind": kind, **_KINDS[kind](case, work)})
    kinds = sorted({row["kind"] for row in rows})
    gates = {kind: all(row["passed"] for row in rows if row["kind"] == kind) for kind in kinds}
    return {
        "schema": "apiforge/economy-hardening-eval/v1",
        "cases": len(rows),
        "gates": gates,
        "passed": all(gates.values()),
        "rows": rows,
    }


__all__ = ["load_cases", "run_hardening"]
