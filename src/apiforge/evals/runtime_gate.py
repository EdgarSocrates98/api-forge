"""Offline quality gate for runtime outcomes and evidence."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from apiforge.evals.suite import EvalResult, evaluate_case, load_cases

REQUIRED_KINDS = frozenset({"golden", "holdout", "mutation"})


def run_runtime_gate(
    cases_path: Path,
    observations: Mapping[str, Mapping[str, Any]],
    *,
    required_kinds: frozenset[str] = REQUIRED_KINDS,
) -> dict[str, object]:
    cases = load_cases(cases_path)
    results: list[EvalResult] = []
    missing_cases: list[str] = []
    for case in cases:
        observation = observations.get(case.case_id)
        if observation is None:
            if case.mandatory:
                missing_cases.append(case.case_id)
            continue
        results.append(
            evaluate_case(
                case,
                observed=str(observation.get("observed", "unresolved")),
                evidence=tuple(str(item) for item in observation.get("evidence", ())),
                axes={str(key): bool(value) for key, value in observation.get("axes", {}).items()},
                holdout_payload=observation.get("holdout_payload"),
            )
        )
    present_kinds = {case.kind for case in cases if case.case_id in observations}
    missing_kinds = tuple(sorted(required_kinds - present_kinds))
    mandatory_results = tuple(
        result
        for result in results
        if next(case for case in cases if case.case_id == result.case_id).mandatory
    )
    failed = tuple(result for result in mandatory_results if result.verdict != "PASS")
    blocked = bool(
        missing_cases or missing_kinds or any(result.verdict == "BLOCKED" for result in failed)
    )
    status = "BLOCKED" if blocked else "REVIEW" if failed else "PASS"
    return {
        "status": status,
        "cases": [result.to_dict() for result in results],
        "missing_cases": tuple(sorted(missing_cases)),
        "missing_kinds": missing_kinds,
        "mandatory_failed": tuple(result.case_id for result in failed),
        "quality_gate": status == "PASS",
        "error_code": "AF-RUNTIME-EVAL-GATE" if blocked else None,
    }
