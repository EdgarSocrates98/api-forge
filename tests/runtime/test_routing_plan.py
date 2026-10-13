from __future__ import annotations

import pytest

from apiforge.contracts.graph_impact import GraphImpactAssessment
from apiforge.contracts.risk_complexity import RiskComplexityAssessment
from apiforge.contracts.routing import RoutingDecision, RoutingPlan, RoutingPolicy
from apiforge.runtime.registry import Capability
from apiforge.runtime.routing import build_routing_plan


def _catalog() -> dict[str, Capability]:
    return {
        "primary": Capability("primary", "agent-primary", "specialist", "read_only"),
        "parallel": Capability("parallel", "agent-parallel", "specialist", "read_only"),
        "reviewer": Capability("reviewer", "agent-reviewer", "reviewer", "read_only"),
        "critic": Capability("critic", "agent-critic", "critic", "read_only"),
        "fallback": Capability("fallback", "agent-fallback", "fallback", "read_only"),
    }


def _decision() -> RoutingDecision:
    return RoutingDecision(
        decision_id="routing:test",
        task_id="task:test",
        revision=1,
        policy_id="routing/v1",
        selected="primary",
        fallback_order=("primary", "parallel", "reviewer", "critic", "fallback"),
    )


def test_parallel_plan_separates_roles_and_is_stable() -> None:
    policy = RoutingPolicy(policy_id="routing/v1", policy_version="routing/v1")

    first = build_routing_plan(_decision(), _catalog(), policy=policy)
    second = build_routing_plan(_decision(), _catalog(), policy=policy)

    assert first.plan_id == second.plan_id
    assert first.primary == "primary"
    assert first.parallel == ("parallel",)
    assert first.reviewers == ("reviewer",)
    assert first.critic == "critic"
    assert first.fallbacks == ("fallback",)
    assert first.challenger_slots == 0
    assert first.challenger_order == ()


def test_sequential_policy_turns_specialists_into_bounded_fallbacks() -> None:
    policy = RoutingPolicy(
        policy_id="routing/v1",
        policy_version="routing/v1",
        execution_mode="sequential_failover",
        max_fallbacks=2,
    )

    plan = build_routing_plan(_decision(), _catalog(), policy=policy)

    assert plan.parallel == ()
    assert plan.fallbacks == ("fallback", "parallel")
    assert plan.reviewers == ("reviewer",)


def test_plan_rejects_duplicate_role_membership() -> None:
    with pytest.raises(ValueError, match="duplicate capabilities"):
        RoutingPlan(
            plan_id="plan:test",
            decision_id="routing:test",
            task_id="task:test",
            revision=1,
            primary="same",
            parallel=("same",),
        )


def test_plan_preserves_graph_assessment_and_merges_verification_effect() -> None:
    graph_impact = GraphImpactAssessment(
        assessment_id="graph-impact:test",
        target_id="service:orders",
        mode="transitive",
        policy_version="graph-impact/v1",
        coverage="complete",
        freshness_state="fresh",
        impact_band="bounded",
        verification_depth="strict",
        required_roles=("reviewer", "critic"),
        gate_state="review",
    )
    risk_assessment = RiskComplexityAssessment(
        assessment_id="risk-assessment:test",
        task_id="task:test",
        revision=1,
        policy_id="routing/v1",
        policy_version="risk-complexity/v1",
        risk="read_only",
        complexity="simple",
        objective_order=("efficiency", "quality"),
        verification_depth="standard",
    )
    decision = _decision().model_copy(
        update={"risk_complexity": risk_assessment, "graph_impact": graph_impact}
    )

    plan = build_routing_plan(
        decision,
        _catalog(),
        policy=RoutingPolicy(policy_id="routing/v1", policy_version="routing/v1"),
    )

    assert plan.graph_impact == graph_impact
    assert plan.verification_depth == "strict"
    assert plan.required_roles == ("critic", "reviewer")
    assert plan.gate_state == "review"
