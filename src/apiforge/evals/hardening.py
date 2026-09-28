"""Economy hardening eval: trust boundary and budget/accounting invariants.

Deterministic, offline cases that pin the review's P1/P2 fixes:

- ``path``: a candidate source path must be allowed or refused by the
  resolver (``..``, absolute, UNC, drive, undeclared repository);
- ``budget``: ``plan_roles`` on an analyzed fixture must fit ``context_bytes``
  (its contract validators run); ``budget_invariant``: the contract refuses a
  plan above the envelope;
- ``tokens``: measured/unmeasured ledger rows give the declared coverage;
- ``phase``: phase usage gives the declared ``budget_status``;
- ``delta``: ``build_delta`` on the analyzed fixture gives the declared status.

The oracle never re-implements the logic it guards.
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


def _spec(root: Path) -> Any:
    from apiforge.contracts.task import Budgets, TaskRisk, TaskSize, TaskSpec, TaskState

    return TaskSpec(
        id="economy-hardening-case",
        outcome="make POST /payments idempotent",
        size=TaskSize.M,
        inputs=(f"project={root / 'proj'}", "target=POST /payments"),
        expected_proofs=("specialist artifact",),
        acceptance_criteria=("plan stays within the envelope",),
        rollback="discard local run artifacts",
        risk=TaskRisk.READ_ONLY,
        state=TaskState.SEALED,
        revision=1,
        budgets=Budgets(max_calls=20),
    )


def _budget(case: dict[str, Any], work: Path, fixture: Path) -> dict[str, Any]:
    """Production path: ``plan_roles`` builds the plan and its contract validators run."""
    from apiforge.runtime.role_context import plan_roles

    context_bytes = int(case["context_bytes"])
    roles = tuple((f"{kind}-{index}", str(kind)) for index, kind in enumerate(case["roles"]))
    try:
        plan = plan_roles(
            fixture, _spec(fixture), roles, context_bytes=context_bytes, run_id=f"eval-{case['id']}"
        )
    except ValueError as exc:
        return {"error": str(exc).splitlines()[0], "passed": False}
    return {
        "total_bytes": plan.total_bytes,
        "context_bytes": context_bytes,
        "capsule": bool(plan.capsule_id),
        "passed": bool(plan.capsule_id) and plan.total_bytes <= context_bytes,
    }


def _budget_invariant(case: dict[str, Any], work: Path, fixture: Path) -> dict[str, Any]:
    """The contract itself must refuse a plan above the envelope."""
    from pydantic import ValidationError

    from apiforge.contracts.selective import RoleContext, RoleContextPlan

    size = int(case["context_bytes"])
    rows = tuple(
        RoleContext(
            role="specialist",
            capability=f"spec-{index}",
            context_class="focused",
            bytes=size,
            budget_bytes=size,
        )
        for index in range(2)
    )
    try:
        RoleContextPlan(run_id="eval", context_bytes=size, roles=rows, total_bytes=2 * size)
    except ValidationError:
        return {"refused": True, "passed": True}
    return {"refused": False, "passed": False}


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


def _delta(case: dict[str, Any], work: Path, fixture: Path) -> dict[str, Any]:
    """Production path: ``build_delta`` on the analyzed fixture."""
    from apiforge.context.delta import UNMAPPED_SOURCE, build_delta

    delta = build_delta(fixture, changed=[str(case["path"])])
    flagged = any(item.startswith(UNMAPPED_SOURCE) for item in delta.unresolved)
    ok = delta.status == case["expect_status"]
    if "expect_unmapped_source" in case:
        ok = ok and flagged is bool(case["expect_unmapped_source"])
    return {"status": delta.status, "unmapped_source": flagged, "passed": ok}


_FIXTURE_KINDS = {"budget": _budget, "budget_invariant": _budget_invariant, "delta": _delta}
_KINDS = {"path": _path, "tokens": _tokens, "phase": _phase}


def run_hardening(corpus: Path, repo_root: Path = Path(".")) -> dict[str, Any]:
    """Budget and delta cases run the production code (never a re-implementation)."""
    from apiforge.evals.extras import _materialize

    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-hardening-") as tmp:
        fixture: Path | None = None
        for index, case in enumerate(load_cases(Path(corpus))):
            kind = str(case.get("kind"))
            work = Path(tmp) / str(index)
            work.mkdir()
            if kind in _FIXTURE_KINDS:
                if fixture is None:
                    fixture = _materialize(
                        Path(repo_root),
                        Path(tmp) / "shared",
                        "tests/fixtures/economy_payments/fastapi",
                        "tests/fixtures/economy_payments/openapi.yaml",
                    )
                row = _FIXTURE_KINDS[kind](case, work, fixture)
            elif kind in _KINDS:
                row = _KINDS[kind](case, work)
            else:
                raise ContractError("AF-EVALS-INVALID", f"unknown case kind {kind!r}")
            rows.append({"case_id": case["id"], "kind": kind, **row})
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
