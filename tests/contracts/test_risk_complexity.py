import pytest
from pydantic import ValidationError

from apiforge.contracts.registry import CONTRACTS
from apiforge.contracts.risk_complexity import (
    RiskComplexityAssessment,
    RiskComplexityPolicy,
    RiskComplexityRule,
    default_risk_complexity_policy,
)


def test_risk_complexity_contract_is_registered() -> None:
    assert CONTRACTS["RiskComplexityAssessment/v1"] is RiskComplexityAssessment


def test_default_policy_contains_all_effect_levels() -> None:
    policy = default_risk_complexity_policy()

    assert set(policy.effects) == {"simple", "moderate", "complex", "critical"}
    assert policy.ordered_rules[0].rule_id == "missing-required-evidence"


def test_policy_rejects_duplicate_rule_ids() -> None:
    with pytest.raises(ValidationError, match="rule ids must be unique"):
        RiskComplexityPolicy(
            policy_version="risk-complexity/test",
            ordered_rules=(
                RiskComplexityRule(
                    rule_id="duplicate",
                    when="size_is_L",
                    complexity="complex",
                ),
                RiskComplexityRule(
                    rule_id="duplicate",
                    when="size_is_M",
                    complexity="moderate",
                ),
            ),
            effects=default_risk_complexity_policy().effects,
        )


def test_assessment_is_frozen_and_preserves_unresolved() -> None:
    assessment = RiskComplexityAssessment(
        assessment_id="risk-assessment:test",
        task_id="task",
        revision=1,
        policy_id="routing/v1",
        policy_version="risk-complexity/v1",
        risk="destructive",
        complexity="critical",
        objective_order=("quality",),
        verification_depth="strict",
        required_roles=("reviewer", "critic", "referee"),
        gate_state="blocked",
        evidence=("task_spec",),
        unresolved=("AF-CAPABILITY-ELIGIBILITY: field=required_evidence; unlock=provide evidence",),
    )

    assert assessment.unresolved
    with pytest.raises(ValidationError):
        assessment.complexity = "simple"  # type: ignore[misc]
