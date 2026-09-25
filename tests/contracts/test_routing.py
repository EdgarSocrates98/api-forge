import pytest
from pydantic import ValidationError

from apiforge.contracts.registry import CONTRACTS
from apiforge.contracts.routing import ObservedSignal, RoutingPolicy, RoutingRequest


def test_routing_contracts_are_registered() -> None:
    assert {
        "ObservedSignal/v1",
        "RoutingPolicy/v1",
        "RoutingRequest/v1",
        "CandidateAssessment/v1",
        "RoutingDecision/v1",
        "ScorecardRoutingAssessment/v1",
        "ScorecardRoutingPolicy/v1",
        "ScorecardShadowEvaluation/v1",
        "ScorecardFeedback/v1",
    } <= set(CONTRACTS)


def test_unknown_signal_cannot_become_a_numeric_zero() -> None:
    with pytest.raises(ValidationError):
        ObservedSignal(name="duration", status="unknown", value=0)


def test_routing_policy_rejects_duplicate_objectives() -> None:
    with pytest.raises(ValidationError):
        RoutingPolicy(
            policy_id="routing/v1",
            policy_version="routing/v1",
            objective_order=("efficiency", "efficiency"),
        )


def test_routing_policy_defaults_to_bounded_scorecard_adaptation() -> None:
    policy = RoutingPolicy(policy_id="routing/v1", policy_version="routing/v1")

    assert policy.scorecard_adaptation.policy_version == "scorecard-routing/v1"
    assert policy.scorecard_adaptation.challenger_slots == 1


def test_routing_request_preserves_declared_evidence() -> None:
    request = RoutingRequest(
        task_id="task",
        revision=1,
        risk="read_only",
        available_evidence=("task_spec",),
        policy_id="routing/v1",
    )
    assert request.available_evidence == ("task_spec",)


def test_routing_request_accepts_additive_complexity_inputs() -> None:
    request = RoutingRequest(
        task_id="task",
        revision=1,
        risk="read_only",
        size="L",
        dependencies=("contract",),
        expected_proofs=("review",),
        strategy="plan-execute-verify",
        policy_id="routing/v1",
    )

    assert request.task_size == "L"
    assert request.dependencies == ("contract",)
