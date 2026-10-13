from pathlib import Path

import yaml

from apiforge.contracts.graph import GraphEdge, GraphNode
from apiforge.graph.impact import assess_graph_impact


def _case(case_id: str) -> dict[str, object]:
    payload = yaml.safe_load(
        Path("tests/fixtures/workspaces/graph_impact_cases.yaml").read_text(encoding="utf-8")
    )
    return next(case for case in payload["cases"] if case["id"] == case_id)


def test_graph_aware_impact_evaluation_cases_are_local_and_replayable() -> None:
    case = _case("direct-chain")
    nodes = tuple(GraphNode.model_validate(item) for item in case["nodes"])
    edges = tuple(GraphEdge.model_validate(item) for item in case["edges"])

    first = assess_graph_impact(nodes, edges, str(case["target"]), mode="transitive")
    second = assess_graph_impact(nodes, edges, str(case["target"]), mode="transitive")

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.assessment_id.startswith("graph-impact:")
    assert all("provider" not in item for item in first.evidence)
