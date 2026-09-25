from apiforge.contracts.agentic import AgentScorecard
from apiforge.contracts.routing import CandidateAssessment
from apiforge.contracts.scorecard_routing import ScorecardRoutingPolicy
from apiforge.runtime.scorecard_routing import assess_scorecard_routing
from apiforge.runtime.scorecard_shadow import evaluate_scorecard_shadow


def _assessment():
    return assess_scorecard_routing(
        (
            CandidateAssessment(capability="champion", agent="agent-champion", eligible=True),
            CandidateAssessment(capability="new", agent="agent-new", eligible=True),
        ),
        {
            "champion": AgentScorecard(
                agent="agent-champion",
                profile_id="champion",
                evaluation_count=2,
                passed_count=2,
                quality_score=0.9,
                quality_promoted=True,
                freshness_state="fresh",
            )
        },
        ScorecardRoutingPolicy(challenger_slots=1),
    )


def test_shadow_evaluation_records_reordering_without_execution() -> None:
    evaluation = evaluate_scorecard_shadow(
        assessment=_assessment(),
        baseline_policy_version="routing/v1",
        baseline_order=("new", "champion"),
        adaptive_order=("champion", "new"),
        baseline_selected="new",
        adaptive_selected="champion",
    )

    assert evaluation.comparison == "reordered"
    assert evaluation.selected_changed is True
    assert evaluation.changed_candidates == ("champion", "new")
    assert evaluation.executed is False


def test_shadow_evaluation_is_replayable() -> None:
    assessment = _assessment()
    kwargs = {
        "assessment": assessment,
        "baseline_policy_version": "routing/v1",
        "baseline_order": ("champion", "new"),
        "adaptive_order": ("champion", "new"),
        "baseline_selected": "champion",
        "adaptive_selected": "champion",
    }

    first = evaluate_scorecard_shadow(**kwargs)
    second = evaluate_scorecard_shadow(**kwargs)

    assert first == second
    assert first.evaluation_id == second.evaluation_id
