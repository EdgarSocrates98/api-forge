"""Economy matrix (§72–76): canonical API tasks × profiles, axes kept apart.

Quality is grounded offline: the deterministic verdict of each contract pair
(OpenAPI ``diff_contracts`` or gRPC ``compare``) against the case's ground
truth, plus the safety invariant — every risk-required role survives the
economy trims. Evidence, cost, context and latency are reported on their own
axes; nothing is blended into one score. Compatible tasks also carry
structural mutants that must flip the verdict to ``breaking``.
"""

from __future__ import annotations

import copy
import json
import statistics
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_evals import (
    CostAxis,
    EconomyMatrix,
    MatrixRow,
    QualityAxis,
    Verdict,
)

PROFILES = ("economy", "balanced", "deep")
NOW = "2026-09-28T00:00:00+00:00"
TASK_ID = "economy-matrix-case"
_UNRESOLVED_CODES = {"AF-OPENAPI-REF-UNRESOLVED", "AF-OPENAPI-UNCLASSIFIED"}
_METHODS = ("get", "put", "post", "delete", "patch")


def load_tasks(corpus: Path) -> list[dict[str, Any]]:
    rows = [
        yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [str(row.get("id")) for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"economy-matrix corpus {corpus} empty or duplicated"
        )
    return rows


# ------------------------------------------------------------------ verdicts
def _openapi_verdict(
    base: Mapping[str, Any], cand: Mapping[str, Any], work: Path
) -> tuple[Verdict, tuple[str, ...], int]:
    from apiforge.openapi.diff import diff_contracts
    from apiforge.openapi.loader import load_openapi

    work.mkdir(parents=True, exist_ok=True)
    before, after = work / "base.yaml", work / "cand.yaml"
    before.write_text(yaml.safe_dump(dict(base), sort_keys=False), encoding="utf-8")
    after.write_text(yaml.safe_dump(dict(cand), sort_keys=False), encoding="utf-8")
    changes = diff_contracts(load_openapi(before), load_openapi(after))
    evidence = tuple(sorted(f"{c.code.value}:{c.method or ''}:{c.path}" for c in changes))
    size = len(json.dumps([c.model_dump(mode="json") for c in changes]).encode("utf-8"))
    if any(c.breaking for c in changes):
        return "breaking", evidence, size
    if any(c.code.value in _UNRESOLVED_CODES for c in changes):
        return "unresolved", evidence, size
    return "compatible", evidence, size


def _grpc_verdict(base: Path, cand: Path) -> tuple[Verdict, tuple[str, ...], int]:
    from apiforge.grpc.compatibility import compare
    from apiforge.grpc.source import load_source

    report = compare(load_source(base), load_source(cand))
    evidence = tuple(sorted(item.code for item in report.diagnostics))
    size = len(report.model_dump_json().encode("utf-8"))
    mapping: dict[str, Verdict] = {"compatible": "compatible", "breaking": "breaking"}
    return mapping.get(report.verdict, "unresolved"), evidence, size


def verdict_for(
    task: Mapping[str, Any], repo_root: Path, work: Path
) -> tuple[Verdict, tuple[str, ...], int]:
    if task["protocol"] == "grpc":
        return _grpc_verdict(repo_root / str(task["baseline"]), repo_root / str(task["candidate"]))
    return _openapi_verdict(task["baseline"], task["candidate"], work)


# ------------------------------------------------------------------ mutants
def _first_operation(doc: Mapping[str, Any]) -> tuple[str, str]:
    for path, item in (doc.get("paths") or {}).items():
        for method in _METHODS:
            if method in item:
                return path, method
    raise ContractError("AF-EVALS-INVALID", "mutant needs at least one operation")


def _schema(doc: dict[str, Any], name: str = "Order") -> dict[str, Any]:
    schema: dict[str, Any] = doc["components"]["schemas"][name]
    return schema


def mutate(doc: Mapping[str, Any], kind: str) -> dict[str, Any]:
    out: dict[str, Any] = copy.deepcopy(dict(doc))
    if kind == "remove_operation":
        path, method = _first_operation(out)
        del out["paths"][path][method]
        if not out["paths"][path]:
            del out["paths"][path]
    elif kind == "remove_response_property":
        schema = _schema(out)
        victim = sorted(set(schema.get("properties") or {}) - set(schema.get("required") or []))
        victim = victim or sorted(schema.get("properties") or {})
        del schema["properties"][victim[0]]
        schema["required"] = [item for item in schema.get("required") or [] if item != victim[0]]
    elif kind == "add_required_request_property":
        schema = _schema(out)
        schema.setdefault("properties", {})["mutant_required"] = {"type": "string"}
        schema["required"] = sorted({*(schema.get("required") or []), "mutant_required"})
    elif kind == "remove_response_status":
        for item in (out.get("paths") or {}).values():
            for method in _METHODS:
                responses = (item.get(method) or {}).get("responses") or {}
                if len(responses) > 1:
                    del responses[max(responses)]
                    return out
        raise ContractError("AF-EVALS-INVALID", "no operation with two responses to remove")
    else:
        raise ContractError("AF-EVALS-INVALID", f"unknown mutant {kind!r}")
    return out


# ------------------------------------------------------------------ runs
def _run(task: Mapping[str, Any], verdict: Verdict, profile: str, root: Path) -> dict[str, Any]:
    from apiforge.contracts.task import Budgets, TaskRisk, TaskSize, TaskSpec, TaskState
    from apiforge.runtime.adapters import FakeModelAdapter
    from apiforge.runtime.runner import run_runtime
    from apiforge.taskspec.store import create

    project = root / "project"
    project.mkdir(parents=True, exist_ok=True)
    (project / "openapi.yaml").write_text("openapi: 3.1.0\n", encoding="utf-8")
    breaking = verdict != "compatible"
    create(
        root,
        TaskSpec(
            id=TASK_ID,
            outcome=str(task.get("outcome", "evaluate the contract change")),
            size=TaskSize.M if breaking else TaskSize.S,
            inputs=(f"project={project}",),
            expected_proofs=("specialist artifact",),
            acceptance_criteria=("findings are evidence bound",),
            rollback="discard local run artifacts",
            risk=TaskRisk.SENSITIVE if breaking else TaskRisk.READ_ONLY,
            state=TaskState.SEALED,
            revision=1,
            budgets=Budgets(max_calls=20),
        ),
    )
    started = time.perf_counter()
    result = run_runtime(root, TASK_ID, adapter=FakeModelAdapter(), now=NOW, profile=profile)
    latency = int((time.perf_counter() - started) * 1000)
    return {"result": result, "latency": latency}


def _row(
    task: Mapping[str, Any],
    profile: str,
    verdict: Verdict,
    evidence: tuple[str, ...],
    evidence_bytes: int,
    run: Mapping[str, Any],
) -> MatrixRow:
    from apiforge.runtime.economy import role_kinds
    from apiforge.runtime.registry import load_capabilities

    result = run["result"]
    run_dir = Path(str(result.get("run_dir", "")))
    economy = result.get("economy") or {}
    plan_path = run_dir / "routing-plan.json"
    missing: tuple[str, ...] = ()
    fanout = 0
    if plan_path.is_file():
        from apiforge.contracts.routing import RoutingPlan

        plan = RoutingPlan.model_validate(json.loads(plan_path.read_text(encoding="utf-8")))
        fanout = len(plan.parallel)
        kinds = {name: item.kind for name, item in load_capabilities().items()}
        economy_plan = json.loads((run_dir / "economy.json").read_text(encoding="utf-8"))
        required = set(economy_plan.get("minimum_roles") or ())
        missing = tuple(sorted(required - role_kinds(plan, kinds)))
    expected = str(task["expected"])
    role_context = result.get("role_context") or {}
    return MatrixRow(
        case_id=str(task["id"]),
        profile=profile,
        holdout=bool(task.get("holdout")),
        status=str(result.get("status", "")),
        quality=QualityAxis(
            verdict=verdict,
            expected=expected,  # type: ignore[arg-type]
            verdict_ok=verdict == expected,
            safety_ok=not missing,
            missing_roles=missing,
        ),
        evidence=evidence,
        cost=CostAxis(
            calls=int(economy.get("calls_used", 0)),
            invocations=len((result.get("run") or {}).get("invocation_ids") or ()),
            fanout=fanout,
            trimmed_roles=tuple(economy.get("trimmed_roles") or ()),
        ),
        context_bytes=int(role_context.get("total_bytes", 0) or 0),
        evidence_bytes=evidence_bytes,
        latency_ms=int(run["latency"]),
    )


def _aggregate(rows: Sequence[MatrixRow]) -> dict[str, dict[str, float]]:
    axes: dict[str, dict[str, float]] = {}
    for profile in PROFILES:
        mine = [row for row in rows if row.profile == profile]
        if not mine:
            continue
        axes[profile] = {
            "quality_rate": round(
                sum(r.quality.verdict_ok and r.quality.safety_ok for r in mine) / len(mine), 4
            ),
            "safety_violations": float(sum(not r.quality.safety_ok for r in mine)),
            "evidence_ids_mean": round(statistics.mean(len(r.evidence) for r in mine), 2),
            "calls_mean": round(statistics.mean(r.cost.calls for r in mine), 2),
            "invocations_mean": round(statistics.mean(r.cost.invocations for r in mine), 2),
            "fanout_mean": round(statistics.mean(r.cost.fanout for r in mine), 2),
            "context_bytes_mean": round(statistics.mean(r.context_bytes for r in mine), 1),
            "latency_ms_median": float(statistics.median(r.latency_ms for r in mine)),
        }
    return axes


def run_matrix(
    corpus: Path,
    repo_root: Path,
    *,
    runner: Callable[[Mapping[str, Any], Verdict, str, Path], dict[str, Any]] = _run,
) -> EconomyMatrix:
    tasks = load_tasks(Path(corpus))
    rows: list[MatrixRow] = []
    mutants_total = 0
    mutants_detected = 0
    with tempfile.TemporaryDirectory(prefix="af-matrix-") as tmp:
        work = Path(tmp)
        for task in tasks:
            verdict, evidence, size = verdict_for(task, Path(repo_root), work / str(task["id"]))
            for profile in PROFILES:
                run = runner(task, verdict, profile, work / f"{task['id']}-{profile}")
                rows.append(_row(task, profile, verdict, evidence, size, run))
            for index, kind in enumerate(task.get("mutants") or ()):
                mutated = dict(task, candidate=mutate(task["candidate"], str(kind)))
                got, _, _ = verdict_for(mutated, Path(repo_root), work / f"{task['id']}-m{index}")
                mutants_total += 1
                mutants_detected += int(got == "breaking")
    axes = _aggregate(rows)
    calls = [axes.get(p, {}).get("calls_mean", 0.0) for p in PROFILES]
    gates = {
        "quality_every_profile": all(axes[p]["quality_rate"] == 1.0 for p in axes),
        "safety_zero_violations": all(axes[p]["safety_violations"] == 0 for p in axes),
        "cost_monotone": calls == sorted(calls),
        "mutation_score": mutants_total > 0 and mutants_detected == mutants_total,
        "holdout_pass": all(
            r.quality.verdict_ok and r.quality.safety_ok for r in rows if r.holdout
        ),
    }
    return EconomyMatrix(
        tasks=len(tasks),
        profiles=PROFILES,
        rows=tuple(rows),
        axes=axes,
        mutation={"total": mutants_total, "detected": mutants_detected},
        gates=gates,
        passed=all(gates.values()),
    )


__all__ = ["PROFILES", "load_tasks", "mutate", "run_matrix", "verdict_for"]
