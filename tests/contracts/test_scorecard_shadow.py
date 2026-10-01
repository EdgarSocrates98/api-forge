import pytest
from pydantic import ValidationError

from apiforge.contracts.scorecard_shadow import ScorecardShadowEvaluation


def test_shadow_contract_requires_same_candidate_set() -> None:
    with pytest.raises(ValidationError, match="same candidate set"):
        ScorecardShadowEvaluation(
            evaluation_id="shadow:1",
            assessment_id="assessment:1",
            baseline_policy_version="routing/v1",
            adaptive_policy_version="scorecard-routing/v1",
            baseline_order=("a",),
            adaptive_order=("b",),
            baseline_selected="a",
            adaptive_selected="b",
            selected_changed=True,
            comparison="reordered",
        )


def test_shadow_contract_is_explicitly_non_executing() -> None:
    evaluation = ScorecardShadowEvaluation(
        evaluation_id="shadow:1",
        assessment_id="assessment:1",
        baseline_policy_version="routing/v1",
        adaptive_policy_version="scorecard-routing/v1",
        baseline_order=("a", "b"),
        adaptive_order=("b", "a"),
        baseline_selected="a",
        adaptive_selected="b",
        selected_changed=True,
        changed_candidates=("a", "b"),
        comparison="reordered",
    )

    assert evaluation.executed is False
    assert "no-capability-invocation" in evaluation.limitations
