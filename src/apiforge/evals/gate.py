"""Evaluation gate (§76): an economy change ships only without quality or safety regression.

Compares two ``EconomyMatrix/v1`` reports row by row (case × profile). Any
safety regression rejects regardless of savings; quality regressions are
tolerated only up to ``max_quality_regression`` (default 0); a lower mutation
score or a regressed holdout case rejects. Savings are reported, never used
to excuse a regression.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_evals import EconomyMatrix, EvaluationGate


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def load_report(path: Path) -> EconomyMatrix:
    try:
        return EconomyMatrix.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        raise _refusal(
            "AF-EVALS-GATE-INVALID",
            f"{path} is not an EconomyMatrix/v1 report: {exc}",
            "report",
            "pass reports written by `apiforge evals economy-matrix --out`",
        ) from exc


def evaluate(
    baseline: EconomyMatrix, candidate: EconomyMatrix, *, max_quality_regression: int = 0
) -> EvaluationGate:
    before = {(row.case_id, row.profile): row for row in baseline.rows}
    after = {(row.case_id, row.profile): row for row in candidate.rows}
    if set(before) != set(after):
        raise _refusal(
            "AF-EVALS-GATE-MISMATCH",
            f"reports cover different case×profile rows ({len(before)} vs {len(after)})",
            "candidate",
            "run both reports on the same corpus",
        )
    quality: list[str] = []
    safety: list[str] = []
    holdout: list[str] = []
    for key in sorted(before):
        old, new = before[key], after[key]
        label = f"{key[0]}@{key[1]}"
        if old.quality.verdict_ok and not new.quality.verdict_ok:
            quality.append(label)
            if new.holdout:
                holdout.append(label)
        if old.quality.safety_ok and not new.quality.safety_ok:
            safety.append(label)
            if new.holdout and label not in holdout:
                holdout.append(label)
    mutation_regression = candidate.mutation.get("detected", 0) < baseline.mutation.get(
        "detected", 0
    ) or (candidate.mutation.get("total", 0) < baseline.mutation.get("total", 0))
    calls_delta = {
        profile: round(
            candidate.axes.get(profile, {}).get("calls_mean", 0.0)
            - baseline.axes.get(profile, {}).get("calls_mean", 0.0),
            2,
        )
        for profile in sorted(set(baseline.axes) | set(candidate.axes))
    }
    reasons: list[str] = []
    if safety:
        reasons.append(f"safety regression on {len(safety)} row(s): never tolerated")
    if len(quality) > max_quality_regression:
        reasons.append(f"{len(quality)} quality regression(s) > allowed {max_quality_regression}")
    if holdout:
        reasons.append(f"holdout regression on {len(holdout)} row(s)")
    if mutation_regression:
        reasons.append("mutation score decreased")
    return EvaluationGate(
        decision="reject" if reasons else "ship",
        quality_regressions=tuple(quality),
        safety_regressions=tuple(safety),
        mutation_regression=mutation_regression,
        holdout_regressions=tuple(holdout),
        max_quality_regression=max_quality_regression,
        calls_delta=calls_delta,
        reasons=tuple(reasons) or ("no regression on quality, safety, holdout or mutation",),
    )


def gate_files(
    baseline: Path, candidate: Path, *, max_quality_regression: int = 0
) -> EvaluationGate:
    return evaluate(
        load_report(baseline), load_report(candidate), max_quality_regression=max_quality_regression
    )


__all__ = ["evaluate", "gate_files", "load_report"]
