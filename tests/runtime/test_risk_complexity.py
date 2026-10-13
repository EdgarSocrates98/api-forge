from pathlib import Path

import yaml

from apiforge.contracts.task import Recipe, TaskRisk, TaskSize, TaskSpec
from apiforge.runtime.registry import load_capabilities, load_profiles
from apiforge.runtime.risk_complexity import assess_risk_complexity
from apiforge.runtime.routing import (
    build_routing_plan,
    build_routing_request,
    load_routing_policy,
    route_capabilities,
)


def _request(
    *,
    risk: TaskRisk = TaskRisk.READ_ONLY,
    size: TaskSize = TaskSize.S,
    available_evidence: tuple[str, ...] = ("task_spec",),
    required_evidence: tuple[str, ...] = (),
    expected_proofs: tuple[str, ...] = (),
    strategy: Recipe = Recipe.DIRECT,
):
    spec = TaskSpec(
        id="complexity-task",
        outcome="route a governed task",
        size=size,
        risk=risk,
        preconditions=required_evidence,
        expected_proofs=expected_proofs,
        strategy=strategy,
        revision=1,
    )
    return build_routing_request(
        spec,
        policy_id="routing/v1",
        available_evidence=available_evidence,
    )


def test_task_size_and_proofs_escalate_complexity_deterministically() -> None:
    policy = load_routing_policy()
    first = assess_risk_complexity(
        _request(size=TaskSize.M, expected_proofs=("proof",)),
        policy,
    )
    second = assess_risk_complexity(
        _request(size=TaskSize.M, expected_proofs=("proof",)),
        policy,
    )

    assert first.complexity == "moderate"
    assert first.verification_depth == "elevated"
    assert first.required_roles == ("reviewer",)
    assert first.assessment_id == second.assessment_id


def test_safety_risk_escalates_to_critical_roles() -> None:
    assessment = assess_risk_complexity(
        _request(risk=TaskRisk.IRREVERSIBLE),
        load_routing_policy(),
    )

    assert assessment.complexity == "critical"
    assert assessment.objective_order == ("quality",)
    assert assessment.required_roles == ("reviewer", "critic", "referee")
    assert assessment.gate_state == "review"


def test_missing_required_evidence_is_blocked_and_visible() -> None:
    assessment = assess_risk_complexity(
        _request(required_evidence=("approval",)),
        load_routing_policy(),
    )

    assert assessment.complexity == "critical"
    assert assessment.gate_state == "blocked"
    assert any("field=required_evidence" in item for item in assessment.unresolved)


def test_complex_routing_adds_reviewer_and_critic_without_reclassifying_primary() -> None:
    policy = load_routing_policy()
    request = _request(size=TaskSize.L)
    decision = route_capabilities(
        load_capabilities(),
        load_profiles(),
        request,
        policy=policy,
    )
    plan = build_routing_plan(decision, load_capabilities(), policy=policy)

    assert decision.risk_complexity is not None
    assert decision.risk_complexity.complexity == "complex"
    assert plan.primary is not None
    assert plan.reviewers == ("task-review",)
    assert plan.critic == "adversarial-critic"
    assert plan.verification_depth == "strict"
    assert plan.gate_state == "review"


def test_fixture_matrix_covers_all_mvp_evaluation_kinds() -> None:
    fixture = yaml.safe_load(
        Path("tests/fixtures/agentic_runtime/risk_complexity_cases.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert {case["kind"] for case in fixture["cases"]} == {
        "golden",
        "holdout",
        "mutation",
        "adversarial",
    }
