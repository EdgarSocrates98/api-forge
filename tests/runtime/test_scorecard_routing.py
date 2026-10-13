from apiforge.contracts.agentic import AgentScorecard
from apiforge.contracts.routing import CandidateAssessment
from apiforge.contracts.scorecard_routing import ScorecardRoutingPolicy
from apiforge.runtime.scorecard_routing import assess_scorecard_routing


def _candidate(name: str) -> CandidateAssessment:
    return CandidateAssessment(capability=name, agent=f"agent-{name}", eligible=True)


def _scorecard(
    name: str,
    *,
    freshness_state: str = "fresh",
    quality_promoted: bool = True,
    quality_score: float = 0.9,
    evaluation_count: int = 2,
) -> AgentScorecard:
    return AgentScorecard(
        agent=f"agent-{name}",
        profile_id=name,
        evaluation_count=evaluation_count,
        passed_count=evaluation_count,
        quality_score=quality_score,
        quality_promoted=quality_promoted,
        freshness_state=freshness_state,  # type: ignore[arg-type]
        evidence=(f"evidence-{name}",),
        computed_from=(f"eval-{name}",),
    )


def test_assessment_prefers_champions_and_bounds_challengers() -> None:
    candidates = (_candidate("champion"), _candidate("new"), _candidate("stale"))
    scorecards = {
        "champion": _scorecard("champion"),
        "stale": _scorecard("stale", freshness_state="stale"),
    }

    assessment = assess_scorecard_routing(
        candidates,
        scorecards,
        ScorecardRoutingPolicy(challenger_slots=1),
    )

    assert assessment.champion_order == ("champion",)
    assert assessment.challenger_order == ("new",)
    assert assessment.selected_challengers == ("new",)
    assert assessment.unresolved_order == ("stale",)
    assert assessment.ordered_candidates == ("champion", "new", "stale")
    assert "stale:scorecard-stale" in assessment.unresolved


def test_unpromoted_history_remains_a_challenger() -> None:
    assessment = assess_scorecard_routing(
        (_candidate("candidate"),),
        {"candidate": _scorecard("candidate", quality_promoted=False)},
        ScorecardRoutingPolicy(),
    )

    record = assessment.candidates[0]
    assert record.lane == "challenger"
    assert record.reason_codes == ("quality-not-promoted",)


def test_missing_history_is_not_coerced_to_zero_quality() -> None:
    assessment = assess_scorecard_routing(
        (_candidate("candidate"),),
        {},
        ScorecardRoutingPolicy(),
    )

    record = assessment.candidates[0]
    assert record.lane == "challenger"
    assert record.quality_score is None
    assert record.reason_codes == ("scorecard-missing",)


def test_assessment_is_replayable_for_identical_candidate_order() -> None:
    candidates = (_candidate("a"), _candidate("b"))
    scorecards = {"a": _scorecard("a"), "b": _scorecard("b", quality_score=0.8)}
    policy = ScorecardRoutingPolicy()

    first = assess_scorecard_routing(candidates, scorecards, policy)
    second = assess_scorecard_routing(candidates, scorecards, policy)

    assert first.assessment_id == second.assessment_id
    assert first.model_dump(mode="json") == second.model_dump(mode="json")
