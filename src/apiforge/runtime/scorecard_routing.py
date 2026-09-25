"""Pure scorecard lane classification and deterministic adaptive ordering."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from apiforge.contracts.agentic import AgentScorecard
from apiforge.contracts.routing import CandidateAssessment
from apiforge.contracts.scorecard_routing import (
    ScorecardCandidateAssessment,
    ScorecardLane,
    ScorecardRoutingAssessment,
    ScorecardRoutingPolicy,
)
from apiforge.core.ids import stable_id


def _scorecard_for(
    candidate: CandidateAssessment,
    scorecards: Mapping[str, AgentScorecard],
) -> AgentScorecard | None:
    return scorecards.get(candidate.capability) or scorecards.get(candidate.agent)


def classify_lane(
    scorecard: AgentScorecard | None,
    *,
    eligible: bool,
    policy: ScorecardRoutingPolicy,
) -> tuple[ScorecardLane, tuple[str, ...]]:
    """Classify history without converting missing evidence into a score."""
    if not eligible:
        return "unresolved", ("candidate-ineligible",)
    if scorecard is None:
        return "challenger", ("scorecard-missing",)
    if scorecard.freshness_state in {"stale", "unresolved"}:
        return "unresolved", (f"scorecard-{scorecard.freshness_state}",)
    if scorecard.freshness_state != "fresh":
        return "challenger", ("scorecard-freshness-unknown",)
    if policy.require_quality_promoted and not scorecard.quality_promoted:
        return "challenger", ("quality-not-promoted",)
    if scorecard.evaluation_count < policy.min_evaluations:
        return "challenger", ("insufficient-evaluations",)
    if scorecard.quality_score < policy.min_quality_score:
        return "challenger", ("quality-below-threshold",)
    return "champion", ("fresh-promoted-scorecard",)


def assess_scorecard_routing(
    candidates: Sequence[CandidateAssessment],
    scorecards: Mapping[str, AgentScorecard],
    policy: ScorecardRoutingPolicy,
) -> ScorecardRoutingAssessment:
    """Return a stable lane assessment over the inherited candidate order."""
    assessments: list[ScorecardCandidateAssessment] = []
    champions: list[str] = []
    challengers: list[str] = []
    unresolved_order: list[str] = []
    evidence: set[str] = set()
    unresolved: set[str] = set()

    for candidate in candidates:
        scorecard = _scorecard_for(candidate, scorecards)
        lane, reasons = classify_lane(scorecard, eligible=candidate.eligible, policy=policy)
        record = ScorecardCandidateAssessment(
            candidate=candidate.capability,
            profile_id=scorecard.profile_id if scorecard is not None else None,
            lane=lane,
            eligible=candidate.eligible,
            quality_score=scorecard.quality_score if scorecard is not None else None,
            evaluation_count=scorecard.evaluation_count if scorecard is not None else 0,
            freshness_state=scorecard.freshness_state if scorecard is not None else "unknown",
            quality_promoted=scorecard.quality_promoted if scorecard is not None else False,
            evidence=scorecard.evidence if scorecard is not None else (),
            computed_from=scorecard.computed_from if scorecard is not None else (),
            gaps=scorecard.gaps if scorecard is not None else (),
            reason_codes=reasons,
        )
        assessments.append(record)
        if scorecard is not None:
            evidence.update(scorecard.evidence)
            evidence.update(scorecard.observation_refs)
            evidence.update(scorecard.computed_from)
            unresolved.update(scorecard.gaps)
        if lane == "champion":
            champions.append(candidate.capability)
        elif lane == "challenger":
            challengers.append(candidate.capability)
        else:
            unresolved_order.append(candidate.capability)
            if scorecard is not None and scorecard.freshness_state in {"stale", "unresolved"}:
                unresolved.add(f"{candidate.capability}:scorecard-{scorecard.freshness_state}")

    selected_challengers = tuple(challengers[: policy.challenger_slots])
    selected_set = set(selected_challengers)
    ordered = tuple(
        [*champions, *selected_challengers]
        + [name for name in challengers if name not in selected_set]
        + unresolved_order
    )
    payload = {
        "policy": policy.model_dump(mode="json"),
        "candidates": [item.model_dump(mode="json") for item in assessments],
        "champion_order": champions,
        "challenger_order": challengers,
        "unresolved_order": unresolved_order,
        "ordered_candidates": ordered,
        "selected_challengers": selected_challengers,
        "evidence": sorted(evidence),
        "unresolved": sorted(unresolved),
    }
    return ScorecardRoutingAssessment(
        assessment_id=stable_id("scorecard-routing", payload),
        policy_version=policy.policy_version,
        candidates=tuple(assessments),
        champion_order=tuple(champions),
        challenger_order=tuple(challengers),
        unresolved_order=tuple(unresolved_order),
        ordered_candidates=ordered,
        selected_challengers=selected_challengers,
        challenger_slots=policy.challenger_slots,
        evidence=tuple(sorted(evidence)),
        unresolved=tuple(sorted(unresolved)),
    )
