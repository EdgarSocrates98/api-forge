import pytest
from pydantic import ValidationError

from apiforge.contracts.registry import CONTRACTS
from apiforge.contracts.scorecard_routing import (
    ScorecardCandidateAssessment,
    ScorecardRoutingAssessment,
    ScorecardRoutingPolicy,
)


def test_scorecard_routing_contracts_are_registered() -> None:
    assert {
        "ScorecardRoutingPolicy/v1",
        "ScorecardCandidateAssessment/v1",
        "ScorecardRoutingAssessment/v1",
    } <= set(CONTRACTS)


def test_champion_requires_fresh_promoted_history() -> None:
    with pytest.raises(ValidationError, match="fresh promoted history"):
        ScorecardCandidateAssessment(
            candidate="contract",
            lane="champion",
            eligible=True,
            freshness_state="stale",
            quality_promoted=True,
            evaluation_count=1,
        )


def test_selected_challengers_cannot_exceed_policy_bound() -> None:
    with pytest.raises(ValidationError, match="selected challengers"):
        ScorecardRoutingAssessment(
            assessment_id="scorecard-routing:test",
            policy_version="scorecard-routing/v1",
            challenger_order=("challenger-a", "challenger-b"),
            selected_challengers=("challenger-a", "challenger-b"),
            challenger_slots=1,
            ordered_candidates=("challenger-a", "challenger-b"),
        )


def test_policy_bounds_challenger_slots() -> None:
    with pytest.raises(ValidationError):
        ScorecardRoutingPolicy(challenger_slots=9)
