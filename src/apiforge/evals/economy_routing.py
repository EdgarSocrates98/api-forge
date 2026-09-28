"""Economy-routing benchmark: profiles vs the pre-economy plan, with the risk floor as invariant.

Each case builds the routing decision for a TaskSpec shape (risk × size), then
compares the pre-economy plan and runtime run against the requested profile.
Plan metrics (roles, fanout, effective profile) are always measured; call
counts come from a fake-adapter runtime run when the TaskSpec passes review,
otherwise the run is reported as ``review-blocked`` rather than guessed.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.routing import RoutingPlan
from apiforge.contracts.task import TaskRisk, TaskSize, TaskSpec, TaskState

NOW = "2026-09-27T00:00:00+00:00"
TASK_ID = "economy-routing-case"
LOW_RISK = {"small", "moderate"}


@dataclass(frozen=True)
class RoutingCase:
    case_id: str
    shape: str
    risk: str
    size: str
    profile: str
    expected_effective: str
    expected_minimum_roles: tuple[str, ...]


def load_cases(corpus: Path) -> list[RoutingCase]:
    cases: list[RoutingCase] = []
    for path in sorted(Path(corpus).glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        expected = raw.get("expected") or {}
        cases.append(
            RoutingCase(
                case_id=str(raw["id"]),
                shape=str(raw["shape"]),
                risk=str(raw["risk"]),
                size=str(raw["size"]),
                profile=str(raw["profile"]),
                expected_effective=str(expected["effective"]),
                expected_minimum_roles=tuple(expected.get("minimum_roles") or ()),
            )
        )
    ids = [case.case_id for case in cases]
    if not cases or len(set(ids)) != len(ids):
        from apiforge.runtime.economy import EconomyError

        raise EconomyError(
            "AF-EVALS-INVALID",
            f"economy-routing corpus {corpus} is empty or has duplicate ids",
            field="corpus",
            unlock="add uniquely named case yaml files",
        )
    return cases


def _task(root: Path, case: RoutingCase) -> TaskSpec:
    from apiforge.taskspec.store import create

    project = root / "project"
    project.mkdir(parents=True, exist_ok=True)
    (project / "openapi.yaml").write_text("openapi: 3.0.0\n", encoding="utf-8")
    return create(
        root,
        TaskSpec(
            id=TASK_ID,
            outcome="produce a reviewed API evolution plan",
            size=TaskSize(case.size),
            inputs=(f"project={project}",),
            expected_proofs=("specialist artifact",),
            acceptance_criteria=("all findings are evidence bound",),
            rollback="discard local run artifacts",
            risk=TaskRisk(case.risk),
            state=TaskState.SEALED,
            revision=1,
        ),
    )


def _fanout(plan: RoutingPlan) -> int:
    return len(plan.parallel) + len(plan.fallbacks) + plan.challenger_slots


def _role_kinds(plan: RoutingPlan, kinds: dict[str, str]) -> list[str]:
    names = [*plan.reviewers, plan.critic, plan.referee]
    return sorted({kinds[name] for name in names if name is not None and name in kinds})


def measure(case: RoutingCase, workdir: Path) -> dict[str, Any]:
    from apiforge.runtime.economy import apply_economy, build_economy_plan
    from apiforge.runtime.registry import load_capabilities, load_profiles
    from apiforge.runtime.routing import (
        build_routing_plan,
        build_routing_request,
        load_routing_policy,
        route_capabilities,
    )
    from apiforge.runtime.runner import run_runtime

    capabilities = load_capabilities()
    kinds = {name: item.kind for name, item in capabilities.items()}
    policy = load_routing_policy()
    spec = _task(workdir / case.case_id / "plan", case)
    request = build_routing_request(
        spec, policy_id=policy.policy_id, available_evidence=("task_spec",)
    )
    decision = route_capabilities(capabilities, load_profiles(), request, policy=policy)
    baseline_plan = build_routing_plan(decision, capabilities, policy=policy)
    economy = build_economy_plan(decision, spec, flag=case.profile, manifest=None)
    plan, economy = apply_economy(baseline_plan, economy, decision, kinds)

    base_root = workdir / case.case_id / "baseline"
    eco_root = workdir / case.case_id / "economy"
    _task(base_root, case)
    _task(eco_root, case)
    base_run = run_runtime(base_root, TASK_ID, now=NOW, economy_enabled=False)
    eco_run = run_runtime(eco_root, TASK_ID, now=NOW, profile=case.profile)
    base_calls = len(base_run["run"]["invocation_ids"])  # type: ignore[index]
    eco_calls = len(eco_run["run"]["invocation_ids"])  # type: ignore[index]
    review_blocked = "findings" in base_run
    raw_block = eco_run.get("economy")
    eco_block: dict[str, Any] = raw_block if isinstance(raw_block, dict) else {}
    return {
        "case_id": case.case_id,
        "shape": case.shape,
        "profile": case.profile,
        "effective": economy.effective,
        "expected_effective": case.expected_effective,
        "minimum_roles": list(economy.minimum_roles),
        "expected_minimum_roles": list(case.expected_minimum_roles),
        "baseline_roles": _role_kinds(baseline_plan, kinds),
        "economy_roles": _role_kinds(plan, kinds),
        "baseline_fanout": _fanout(baseline_plan),
        "economy_fanout": _fanout(plan),
        "trimmed_roles": list(economy.trimmed_roles),
        "runtime": "review-blocked" if review_blocked else "ran",
        "baseline_calls": None if review_blocked else base_calls,
        "economy_calls": None if review_blocked else eco_calls,
        "economy_status": eco_block.get("status"),
        "stopped_at": eco_block.get("stopped_at"),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    role_violations = [
        row["case_id"]
        for row in rows
        if not set(row["baseline_roles"]) <= set(row["economy_roles"])
        or sorted(row["minimum_roles"]) != sorted(row["expected_minimum_roles"])
    ]
    profile_mismatch = [
        row["case_id"] for row in rows if row["effective"] != row["expected_effective"]
    ]
    critical_not_deep = [
        row["case_id"] for row in rows if row["shape"] == "critical" and row["effective"] != "deep"
    ]
    economy_not_cheaper = [
        row["case_id"]
        for row in rows
        if row["shape"] in LOW_RISK
        and row["profile"] == "economy"
        and not (
            row["economy_fanout"] < row["baseline_fanout"]
            and (row["economy_calls"] is None or row["economy_calls"] <= row["baseline_calls"])
        )
    ]
    gates = {
        "role_invariant": not role_violations,
        "effective_profile": not profile_mismatch,
        "critical_is_deep": not critical_not_deep,
        "economy_cheaper_low_risk": not economy_not_cheaper,
    }
    return {
        "schema": "apiforge/economy-routing-eval/v1",
        "cases": len(rows),
        "gates": gates,
        "passed": all(gates.values()),
        "role_violations": role_violations,
        "profile_mismatch": profile_mismatch,
        "critical_not_deep": critical_not_deep,
        "economy_not_cheaper": economy_not_cheaper,
        "rows": rows,
    }


def run_economy_routing(
    corpus: Path, *, measure_case: Callable[[RoutingCase, Path], dict[str, Any]] = measure
) -> dict[str, Any]:
    cases = load_cases(corpus)
    with tempfile.TemporaryDirectory(prefix="af-economy-routing-") as tmp:
        rows = [measure_case(case, Path(tmp)) for case in cases]
    return summarize(rows)


__all__ = ["RoutingCase", "load_cases", "measure", "run_economy_routing", "summarize"]
