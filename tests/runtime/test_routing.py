from pathlib import Path

import yaml

from apiforge.contracts.graph import GraphEdge, GraphNode
from apiforge.contracts.routing import ObservedSignal
from apiforge.contracts.task import TaskRisk, TaskSpec
from apiforge.runtime.registry import load_capabilities, load_profiles
from apiforge.runtime.routing import (
    build_routing_request,
    load_routing_policy,
    route_capabilities,
)


def _request(*, risk: TaskRisk = TaskRisk.READ_ONLY):
    return build_routing_request(
        TaskSpec(
            id="routing-task",
            outcome="route a task",
            risk=risk,
            revision=1,
        ),
        policy_id="routing/v1",
        available_evidence=("task_spec",),
    )


def test_routing_fixture_prioritizes_observed_efficiency() -> None:
    fixture = yaml.safe_load(
        Path("tests/fixtures/agentic_runtime/routing_cases.yaml").read_text(encoding="utf-8")
    )
    signals = {
        capability: (
            ObservedSignal(
                name="duration",
                value=value["duration"],
                status="observed",
                unit="ms",
            ),
        )
        for capability, value in fixture["cases"][0]["signals"].items()
    }
    decision = route_capabilities(
        load_capabilities(),
        load_profiles(),
        _request(),
        policy=load_routing_policy(),
        signals=signals,
    )
    assert decision.selected == "api-performance-review"
    assert decision.fallback_order[0] == "api-performance-review"
    assert decision.risk_complexity is not None
    assert decision.risk_complexity.complexity == "simple"
    assert decision.scorecard_routing is not None
    assert decision.scorecard_routing.selected_challengers
    selected = next(item for item in decision.candidates if item.capability == decision.selected)
    assert selected.ranking_key


def test_routing_rejects_unsafe_candidates_before_ranking() -> None:
    decision = route_capabilities(
        load_capabilities(),
        load_profiles(),
        _request(risk=TaskRisk.SENSITIVE),
        policy=load_routing_policy(),
    )
    assert (
        decision.selected == "api-adversarial-critic" or decision.selected == "api-security-review"
    )
    rejected = {item.capability: item for item in decision.candidates if not item.eligible}
    assert rejected["api-contract-review"].rejection is not None
    assert rejected["api-contract-review"].rejection["field"] == "profile.accepted_risks"


def test_routing_records_unknown_signals_and_replays_deterministically() -> None:
    first = route_capabilities(
        load_capabilities(), load_profiles(), _request(), policy=load_routing_policy()
    )
    second = route_capabilities(
        load_capabilities(), load_profiles(), _request(), policy=load_routing_policy()
    )
    assert first.fallback_order == second.fallback_order
    assert first.decision_id == second.decision_id
    assert any(item.endswith(":duration:unresolved") for item in first.unresolved)
    assert first.risk_complexity is not None
    assert first.risk_complexity.assessment_id == second.risk_complexity.assessment_id
    assert first.scorecard_routing == second.scorecard_routing


def test_routing_preserves_eligibility_refusal_when_no_candidate_exists() -> None:
    request = build_routing_request(
        TaskSpec(
            id="routing-task",
            outcome="route a task",
            risk=TaskRisk.IRREVERSIBLE,
            preconditions=("unavailable-evidence",),
            revision=1,
        ),
        policy_id="routing/v1",
        available_evidence=("task_spec",),
    )
    decision = route_capabilities(
        load_capabilities(), load_profiles(), request, policy=load_routing_policy()
    )
    assert decision.selected is None
    assert any(item.startswith("AF-CAPABILITY-ELIGIBILITY") for item in decision.unresolved)


def test_graph_impact_adds_a_canonical_gate_and_prefers_explicit_candidate() -> None:
    request = build_routing_request(
        TaskSpec(
            id="routing-graph-task",
            outcome="route a graph-aware task",
            risk=TaskRisk.READ_ONLY,
            revision=1,
        ),
        policy_id="routing/v1",
        available_evidence=("task_spec",),
        graph_target="service:orders",
        graph_mode="transitive",
        graph_candidate_refs={
            "api-performance-review": ("agent:api-performance-review",),
            "api-contract-review": ("agent:api-contract-review",),
        },
    )
    nodes = (
        GraphNode(id="service:orders", kind="service"),
        GraphNode(id="agent:api-performance-review", kind="agent"),
        GraphNode(id="agent:api-contract-review", kind="agent"),
    )
    edges = (
        GraphEdge(
            from_id="agent:api-performance-review",
            to_id="service:orders",
            kind="affects",
        ),
    )

    decision = route_capabilities(
        load_capabilities(),
        load_profiles(),
        request,
        policy=load_routing_policy(),
        graph_nodes=nodes,
        graph_edges=edges,
    )

    assert decision.graph_impact is not None
    assert decision.graph_impact.impact_band == "explicit"
    assert decision.selected == "api-performance-review"
    assert decision.graph_impact.candidate_impacts[0].matched == "none"
    assert any(
        item.candidate == "api-performance-review" and item.matched == "explicit"
        for item in decision.graph_impact.candidate_impacts
    )


def test_graph_impact_is_optional_for_legacy_routing() -> None:
    decision = route_capabilities(
        load_capabilities(),
        load_profiles(),
        _request(),
        policy=load_routing_policy(),
    )

    assert decision.graph_impact is None
