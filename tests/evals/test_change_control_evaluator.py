from __future__ import annotations

from apiforge.contracts.change_control import Recommendation
from apiforge.evals.change_control import evaluate_recommendation


def test_change_control_recommendation_evaluation_passes() -> None:
    recommendation = Recommendation(
        recommendation="review",
        evidence_refs=("case.json",),
        verifier="apiforge change-control verify",
        confidence=0.8,
    )
    evaluation = evaluate_recommendation(recommendation, required_evidence=("case.json",))
    assert evaluation.status == "pass"
