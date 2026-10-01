import pytest
from pydantic import ValidationError

from apiforge.contracts.graph_impact import (
    GraphImpactAssessment,
    GraphImpactPolicy,
    default_graph_impact_policy,
)
from apiforge.contracts.registry import CONTRACTS


def test_graph_impact_contracts_are_registered() -> None:
    assert {
        "GraphImpactPolicy/v1",
        "GraphImpactEffect/v1",
        "GraphImpactNode/v1",
        "GraphCandidateImpact/v1",
        "GraphImpactAssessment/v1",
    } <= set(CONTRACTS)


def test_default_policy_is_bounded_and_complete() -> None:
    policy = default_graph_impact_policy()

    assert policy.policy_version == "graph-impact/v1"
    assert policy.max_depth == 4
    assert set(policy.effects) == {"none", "explicit", "bounded", "unresolved"}


def test_policy_rejects_missing_effect_band() -> None:
    values = default_graph_impact_policy().model_dump(mode="python")
    values["effects"].pop("unresolved")

    with pytest.raises(ValidationError):
        GraphImpactPolicy.model_validate(values)


def test_assessment_rejects_duplicate_impacted_nodes() -> None:
    with pytest.raises(ValidationError):
        GraphImpactAssessment(
            assessment_id="graph-impact:test",
            target_id="service:orders",
            mode="direct",
            policy_version="graph-impact/v1",
            coverage="complete",
            freshness_state="fresh",
            impact_band="explicit",
            impacted_nodes=(
                {"node_id": "operation:orders", "kind": "operation", "depth": 1},
                {"node_id": "operation:orders", "kind": "operation", "depth": 1},
            ),
        )
