"""Deterministic control-plane evals: §28-§32 lifecycle vs declared cases."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agentic import ApprovalGate
from apiforge.contracts.agentic_governance import PromotionEvidence
from apiforge.contracts.base import ContractError
from apiforge.economy.run_ledger import EconomyError
from apiforge.governance.control_plane import (
    demote,
    evaluate_route,
    load_routes,
    promote,
)


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"control-plane corpus {corpus} empty or duplicated"
        )
    return cases


def _write_routes(directory: Path, rows: list[dict[str, Any]]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "routes.yaml"
    lines = ["version: 1", "routes:"]
    for row in rows:
        lines.append(f"  - route: {row['route']}")
        lines.append(f"    mode: {row.get('mode', 'shadow')}")
        lines.append(f"    candidate: {row.get('candidate', 'candidate')}")
        lines.append(f"    legacy: {row.get('legacy', 'legacy')}")
        fallback = row.get("fallback_route")
        lines.append(f"    fallback_route: {fallback if fallback else 'null'}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _run_case(case: dict[str, Any], root: Path) -> dict[str, Any]:
    failures: list[str] = []
    routes = load_routes(_write_routes(root, case.get("routes") or []))
    expect = case.get("expect") or {}
    for step in case.get("steps") or ():
        op = step["op"]
        if op == "eval":
            try:
                decision = evaluate_route(
                    root,
                    step["route"],
                    candidate_decision=step.get("candidate") or {},
                    legacy_decision=step.get("legacy") or {},
                    confidence=step.get("confidence"),
                    evidence_refs=tuple(step.get("evidence") or ()),
                    triggers=tuple(step.get("triggers") or ()),
                    routes=routes,
                )
                wanted = step.get("expect") or {}
                for key, value in wanted.items():
                    actual: Any
                    if key == "fallback_action":
                        actual = decision.fallback.action if decision.fallback else None
                    elif key == "fallback_code":
                        actual = decision.fallback.code if decision.fallback else None
                    else:
                        actual = getattr(decision, key)
                    if actual != value:
                        failures.append(f"eval.{key} {actual} != {value}")
            except EconomyError as exc:
                if step.get("expect_code") not in str(exc):
                    failures.append(f"eval raised {exc.code}, wanted {step.get('expect_code')}")
        elif op == "promote":
            try:
                evidence = PromotionEvidence.model_validate(step.get("evidence") or {})
                gate = (
                    ApprovalGate.model_validate(step["approval"]) if step.get("approval") else None
                )
                promote_decision = promote(
                    root, step["route"], evidence, approval=gate, routes=routes
                )
                wanted = step.get("expect") or {}
                if "allowed" in wanted and promote_decision.allowed != wanted["allowed"]:
                    failures.append(
                        f"promote.allowed {promote_decision.allowed} != {wanted['allowed']}"
                    )
                if "code" in wanted and promote_decision.code != wanted["code"]:
                    failures.append(
                        f"promote.code {promote_decision.code} != {wanted['code']}"
                    )
                if "to_mode" in wanted and promote_decision.to_mode != wanted["to_mode"]:
                    failures.append(
                        f"promote.to_mode {promote_decision.to_mode} != {wanted['to_mode']}"
                    )
            except EconomyError as exc:
                if step.get("expect_code") not in str(exc):
                    failures.append(f"promote raised {exc.code}, wanted {step.get('expect_code')}")
        elif op == "demote":
            demote(root, step["route"], routes=routes)
    if "final_mode" in expect:
        from apiforge.governance.control_plane import route_status

        final = route_status(root, expect["route"], routes=routes).mode
        if final != expect["final_mode"]:
            failures.append(f"final mode {final} != {expect['final_mode']}")
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_control_plane(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-control-evals-") as tmp:
        for index, case in enumerate(cases):
            results.append(_run_case(case, Path(tmp) / str(index)))
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/control-plane-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_control_plane"]
