"""Deterministic model-routing evals: §33-§35 vs declared cases."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.model_routing import (
    ModelCandidate,
    ModelEvaluation,
    ModelRouteInputs,
)
from apiforge.runtime.model_router import route_model
from apiforge.runtime.model_scorecard import aggregate_scorecards, scorecard_map


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError(
            "AF-EVALS-INVALID", f"model-routing corpus {corpus} empty or duplicated"
        )
    return cases


def _run_case(case: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    inputs = ModelRouteInputs.model_validate(case.get("inputs") or {})
    candidates = tuple(ModelCandidate.model_validate(row) for row in case.get("candidates") or ())
    rows = [ModelEvaluation.model_validate(row) for row in case.get("evaluations") or ()]
    cards = scorecard_map(aggregate_scorecards(rows), task_class=case.get("task_class"))
    policy = case.get("policy") or {}
    merged = {
        "quality_floor": float(policy.get("quality_floor", 0.8)),
        "min_evaluations": int(policy.get("min_evaluations", 3)),
        "weights": policy.get("weights")
        or {"quality": 0.45, "latency": 0.15, "cost": 0.25, "availability": 0.15},
    }
    decision = route_model(inputs, candidates, cards, policy=merged)
    expect = case.get("expect") or {}
    if "selected" in expect and decision.selected != expect["selected"]:
        failures.append(f"selected {decision.selected} != {expect['selected']}")
    if "code" in expect and decision.code != expect["code"]:
        failures.append(f"code {decision.code} != {expect['code']}")
    for model, wanted in (expect.get("ineligible") or {}).items():
        ranked = next((r for r in decision.ranked if r.model == model), None)
        if ranked is None:
            failures.append(f"model {model} absent from ranking")
        elif ranked.eligible:
            failures.append(f"model {model} unexpectedly eligible")
        else:
            missing = [reason for reason in wanted if reason not in ranked.reasons]
            if missing:
                failures.append(f"model {model} missing reasons {missing}")
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_model_routing(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results = [_run_case(case) for case in cases]
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/model-routing-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_model_routing"]
