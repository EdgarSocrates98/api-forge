"""Deterministic agent quality scorecards derived from evaluation results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, cast

from apiforge.contracts.agentic import AgentCapabilityProfile, AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.contracts.routing import ObservedSignal
from apiforge.evals.suite import EvalResult


def build_scorecard(
    profile: AgentCapabilityProfile,
    results: tuple[EvalResult, ...],
    *,
    observations: tuple[ObservedSignal, ...] = (),
    allow_quality_promotion: bool = True,
) -> AgentScorecard:
    scores = tuple(result.score for result in results)
    passed = sum(result.verdict == "PASS" for result in results)
    gaps = tuple(
        sorted(
            {
                *(item for result in results for item in result.missing_evidence),
                *(item for result in results for item in result.failed_axes),
            }
        )
    )
    last = cast(
        Literal["unknown", "PASS", "REVIEW", "BLOCKED"],
        results[-1].verdict if results else "unknown",
    )
    costs = tuple(
        item.value
        for item in observations
        if item.name == "cost" and item.status == "observed" and item.value is not None
    )
    durations = tuple(
        item.value
        for item in observations
        if item.name == "duration" and item.status == "observed" and item.value is not None
    )
    tokens = tuple(
        item.value
        for item in observations
        if item.name == "cost" and item.unit == "tokens" and item.status == "observed" and item.value is not None
    )
    dimension_scores = {
        axis: round(
            sum(axis not in result.failed_axes for result in results) / len(results),
            3,
        )
        for axis in profile.quality_axes
        if results
    }
    freshness_states = {item.freshness_state for item in observations}
    freshness_state = (
        "stale"
        if "stale" in freshness_states
        else "unresolved"
        if "unresolved" in freshness_states
        else "fresh"
        if "fresh" in freshness_states
        else "unknown"
    )
    promotion_allowed = allow_quality_promotion and not freshness_states.intersection(
        {"stale", "unresolved"}
    )
    return AgentScorecard(
        agent=profile.agent,
        profile_id=profile.profile_id,
        evaluation_count=len(results),
        passed_count=passed,
        quality_score=round(sum(scores) / len(scores), 3)
        if scores and promotion_allowed
        else 0.0,
        quality_promoted=bool(results) and promotion_allowed,
        observed_cost=round(sum(costs) / len(costs), 3) if costs else None,
        observed_duration_ms=round(sum(durations) / len(durations), 3) if durations else None,
        observed_tokens=round(sum(tokens) / len(tokens), 3) if tokens else None,
        dimension_scores=dimension_scores,
        freshness_state=freshness_state,
        observed_at=next((item.observed_at for item in observations if item.observed_at), None),
        expires_at=next((item.expires_at for item in observations if item.expires_at), None),
        observation_refs=tuple(
            sorted({ref for item in observations for ref in item.evidence_refs})
        ),
        last_verdict=last,
        evidence=tuple(sorted({item for result in results for item in result.evidence})),
        gaps=gaps,
        computed_from=tuple(result.case_id for result in results),
    )


def save_scorecard(root: Path, scorecard: AgentScorecard) -> Path:
    directory = Path(root) / ".apiforge" / "scorecards"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{scorecard.profile_id}.json"
    path.write_text(
        json.dumps(scorecard.model_dump(mode="json"), sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_scorecards(root: Path) -> tuple[AgentScorecard, ...]:
    directory = Path(root) / ".apiforge" / "scorecards"
    if not directory.is_dir():
        return ()
    records: list[AgentScorecard] = []
    for path in sorted(directory.glob("*.json")):
        try:
            records.append(
                AgentScorecard.model_validate(json.loads(path.read_text(encoding="utf-8")))
            )
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise ContractError("AF-SCORECARD-INVALID", f"{path}: {exc}") from exc
    return tuple(records)
