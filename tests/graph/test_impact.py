from pathlib import Path

import pytest
import yaml

from apiforge.contracts.graph import GraphEdge, GraphNode, NodeKind
from apiforge.contracts.graph_impact import default_graph_impact_policy
from apiforge.graph.impact import assess_graph_impact


def _cases() -> dict[str, dict[str, object]]:
    payload = yaml.safe_load(
        Path("tests/fixtures/workspaces/graph_impact_cases.yaml").read_text(encoding="utf-8")
    )
    return {str(case["id"]): case for case in payload["cases"]}


def _graph(case_id: str) -> tuple[str, tuple[GraphNode, ...], tuple[GraphEdge, ...]]:
    case = _cases()[case_id]
    nodes = tuple(GraphNode.model_validate(item) for item in case["nodes"])
    edges = tuple(GraphEdge.model_validate(item) for item in case["edges"])
    return str(case["target"]), nodes, edges


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("direct", ("operation:orders",)),
        ("transitive", ("operation:orders", "route:orders")),
        ("all", ("operation:orders", "route:orders")),
    ],
)
def test_impact_modes_are_bounded_and_canonical(mode: str, expected: tuple[str, ...]) -> None:
    target, nodes, edges = _graph("direct-chain")

    assessment = assess_graph_impact(nodes, edges, target, mode=mode)

    assert tuple(item.node_id for item in assessment.impacted_nodes) == expected
    assert assessment.coverage == "complete"
    assert assessment.unresolved == ()


def test_impact_replays_to_identical_bytes() -> None:
    target, nodes, edges = _graph("direct-chain")

    first = assess_graph_impact(nodes, edges, target, mode="transitive")
    second = assess_graph_impact(
        tuple(reversed(nodes)), tuple(reversed(edges)), target, mode="transitive"
    )

    assert first.assessment_id == second.assessment_id
    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_cycle_and_budget_are_visible() -> None:
    target, nodes, edges = _graph("cycle-and-budget")
    cycle_assessment = assess_graph_impact(nodes, edges, target)
    assert any(value.startswith("cycle:") for value in cycle_assessment.limitations)

    policy = default_graph_impact_policy().model_copy(update={"max_nodes": 1})

    assessment = assess_graph_impact(nodes, edges, target, policy=policy)

    assert assessment.coverage == "partial"
    assert assessment.impact_band == "bounded"
    assert any(value.startswith("max_nodes:") for value in assessment.limitations)


def test_missing_target_uses_conservative_fallback() -> None:
    target, nodes, edges = _graph("unresolved-target")

    assessment = assess_graph_impact(
        nodes,
        edges,
        target,
        candidate_refs={"api-contract-review": ("agent:missing",)},
    )

    assert assessment.coverage == "missing"
    assert assessment.impact_band == "unresolved"
    assert assessment.verification_depth in {"elevated", "strict"}
    assert any(value.endswith(":missing") for value in assessment.unresolved)
    assert assessment.candidate_impacts[0].matched == "unresolved"


def test_stale_graph_preserves_explicit_nodes_and_gap() -> None:
    target, nodes, edges = _graph("direct-chain")

    assessment = assess_graph_impact(
        nodes,
        edges,
        target,
        freshness_state="stale",
    )

    assert assessment.coverage == "partial"
    assert assessment.impacted_nodes
    assert "graph:freshness:stale" in assessment.unresolved
    assert assessment.verification_depth in {"elevated", "strict"}


@pytest.mark.parametrize("kind", tuple(NodeKind))
def test_all_closed_node_kinds_are_preserved(kind: NodeKind) -> None:
    target_id = f"target:{kind.value}"
    dependent_id = f"dependent:{kind.value}"
    assessment = assess_graph_impact(
        (
            GraphNode(id=target_id, kind=kind),
            GraphNode(id=dependent_id, kind=NodeKind.EVIDENCE),
        ),
        (GraphEdge(from_id=dependent_id, to_id=target_id, kind="affects"),),
        target_id,
        mode="direct",
    )

    assert assessment.target_kind is kind
    assert assessment.impacted_nodes[0].kind is NodeKind.EVIDENCE
