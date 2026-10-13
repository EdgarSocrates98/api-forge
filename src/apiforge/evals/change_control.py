"""Deterministic evaluation helpers for change-control recommendations."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from apiforge.contracts.change_control import Recommendation, RecommendationEvaluation
from apiforge.core.io import read_json


def _required_fields(value: Recommendation) -> tuple[str, ...]:
    return tuple(
        name
        for name in (
            "recommendation",
            "facts",
            "assumptions",
            "alternatives",
            "risks",
            "unresolved",
            "evidence_refs",
            "verifier",
            "confidence",
        )
        if getattr(value, name) in (None, "")
    )


def evaluate_recommendation(
    recommendation: Recommendation,
    *,
    dataset: str = "api-git-cicd",
    case_id: str = "change-control",
    required_evidence: Iterable[str] = (),
) -> RecommendationEvaluation:
    missing = tuple(item for item in required_evidence if item not in recommendation.evidence_refs)
    missing = (*missing, *_required_fields(recommendation))
    if missing:
        return RecommendationEvaluation(
            status="fail",
            dataset=dataset,
            case_id=case_id,
            missing_requirements=tuple(sorted(set(missing))),
            notes=("recommendation contract or declared evidence is incomplete",),
        )
    return RecommendationEvaluation(
        status="pass",
        dataset=dataset,
        case_id=case_id,
        matched_requirements=("recommendation", "evidence", "verifier"),
    )


def required_evidence_from_golden(path: Path) -> tuple[str, ...]:
    raw = read_json(path)
    if not isinstance(raw, dict):
        return ()
    values = raw.get("required_evidence", ())
    return tuple(str(item) for item in values) if isinstance(values, list) else ()
