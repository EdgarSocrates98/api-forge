import pytest
from pydantic import ValidationError

from apiforge.contracts.economy import BudgetEnvelope, EconomyPlan
from apiforge.contracts.registry import CONTRACTS
from apiforge.contracts.routing import RoutingDecision
from apiforge.contracts.workspace import ProjectManifest


def test_registry_exposes_economy_routing_contracts() -> None:
    for name in ("BudgetEnvelope/v1", "EconomyPlan/v1", "LadderStep/v1", "RiskClassification/v1"):
        assert name in CONTRACTS


def test_legacy_routing_decision_payload_still_validates() -> None:
    legacy = {"decision_id": "d", "task_id": "t", "revision": 1, "policy_id": "p"}
    decision = RoutingDecision.model_validate(legacy)
    assert decision.economy is None


def test_legacy_project_manifest_still_validates() -> None:
    manifest = ProjectManifest.model_validate({"project_id": "p", "root": "."})
    assert manifest.economy_profile is None


def test_envelope_forbids_silent_downgrade() -> None:
    with pytest.raises(ValidationError):
        BudgetEnvelope(
            profile="economy",
            provider_calls=4,
            fanout=0,
            fallbacks=0,
            debate_rounds=0,
            challenger_slots=0,
            verification_share=0.25,
            ladder_ceiling="L3",
            silent_downgrade=True,
        )


def test_economy_plan_rejects_unknown_profile() -> None:
    with pytest.raises(ValidationError):
        EconomyPlan.model_validate(
            {
                "requested": "cheap",
                "requested_source": "flag",
                "floor": "economy",
                "effective": "economy",
                "envelope": {
                    "profile": "economy",
                    "provider_calls": 4,
                    "fanout": 0,
                    "fallbacks": 0,
                    "debate_rounds": 0,
                    "challenger_slots": 0,
                    "verification_share": 0.25,
                    "ladder_ceiling": "L3",
                },
            }
        )
