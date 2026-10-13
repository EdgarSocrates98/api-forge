import pytest
from pydantic import ValidationError

from apiforge.contracts.registry import CONTRACTS
from apiforge.contracts.routing_evolution import (
    EvidenceCoverage,
    EvolutionPolicy,
    PromotionGate,
)


def test_evolution_contracts_are_registered() -> None:
    assert {
        "EvidenceCoverage/v1",
        "EvolutionPolicy/v1",
        "PromotionGate/v1",
        "RoutingEvolution/v1",
    } <= set(CONTRACTS)


def test_coverage_rejects_inconsistent_missing_values() -> None:
    with pytest.raises(ValidationError, match="missing evidence"):
        EvidenceCoverage(
            required=("routing",),
            available=(),
            missing=(),
            state="missing",
        )


def test_active_gate_requires_local_proof_and_rollback() -> None:
    coverage = EvidenceCoverage(
        required=("routing",),
        available=("routing",),
        missing=(),
        state="complete",
    )
    with pytest.raises(ValidationError, match="only local mode"):
        PromotionGate(
            decision_id="routing:1",
            mode="replay",
            state="active",
            coverage=coverage,
            evidence_refs=("routing",),
            policy_version="routing-evolution/wave-0",
            rollback_ref="run:1:static-routing",
        )


def test_adaptive_policy_requires_an_explicit_bound() -> None:
    with pytest.raises(ValidationError, match="max_steps"):
        EvolutionPolicy(adaptive_plan_enabled=True)


def test_evolution_policy_rejects_external_mutation() -> None:
    with pytest.raises(ValidationError, match="external mutation"):
        EvolutionPolicy(allow_external_mutation=True)
