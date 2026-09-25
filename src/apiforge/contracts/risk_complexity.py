"""Versioned contracts for deterministic task risk and complexity policy."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract

ComplexityLevel = Literal["simple", "moderate", "complex", "critical"]
VerificationDepth = Literal["standard", "elevated", "strict"]
ReviewRole = Literal["reviewer", "critic", "referee"]
RoutingObjectiveName = Literal["efficiency", "quality"]
RiskComplexityGate = Literal["open", "review", "blocked"]
RiskComplexityPredicate = Literal[
    "required_evidence_unavailable",
    "required_expertise_unavailable",
    "size_is_L",
    "size_is_M",
    "dependencies_present",
    "expected_proofs_present",
    "strategy_requires_verification",
]


class RiskComplexityEffect(VersionedContract):
    """Policy effects associated with one complexity level."""

    objective_order: tuple[RoutingObjectiveName, ...]
    verification_depth: VerificationDepth
    required_roles: tuple[ReviewRole, ...] = ()

    @model_validator(mode="after")
    def effect_values_are_unique(self) -> RiskComplexityEffect:
        if len(set(self.objective_order)) != len(self.objective_order):
            raise ValueError("risk complexity objective_order must not contain duplicates")
        if len(set(self.required_roles)) != len(self.required_roles):
            raise ValueError("risk complexity required_roles must not contain duplicates")
        return self


class RiskComplexityRule(VersionedContract):
    """One ordered, explicit predicate that may increase complexity."""

    rule_id: str = Field(min_length=1)
    when: RiskComplexityPredicate
    complexity: ComplexityLevel


class RiskComplexityPolicy(VersionedContract):
    """Local policy data used by the pure risk/complexity classifier."""

    policy_version: str = Field(min_length=1)
    unknown_behavior: Literal["unresolved"] = "unresolved"
    risk_overrides: Mapping[str, ComplexityLevel] = {}
    ordered_rules: tuple[RiskComplexityRule, ...] = ()
    effects: Mapping[ComplexityLevel, RiskComplexityEffect]

    @model_validator(mode="after")
    def policy_is_complete(self) -> RiskComplexityPolicy:
        ids = [rule.rule_id for rule in self.ordered_rules]
        if len(set(ids)) != len(ids):
            raise ValueError("risk complexity rule ids must be unique")
        missing = {"simple", "moderate", "complex", "critical"} - set(self.effects)
        if missing:
            raise ValueError(f"risk complexity effects missing: {sorted(missing)}")
        return self


class RiskComplexityAssessment(VersionedContract):
    """Immutable explanation of the routing effects selected by local policy."""

    assessment_id: str
    task_id: str
    revision: int = Field(ge=0)
    policy_id: str
    policy_version: str
    risk: str
    complexity: ComplexityLevel
    factors: tuple[str, ...] = ()
    objective_order: tuple[RoutingObjectiveName, ...]
    verification_depth: VerificationDepth
    required_roles: tuple[ReviewRole, ...] = ()
    gate_state: RiskComplexityGate = "open"
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()

    @model_validator(mode="after")
    def assessment_values_are_unique(self) -> RiskComplexityAssessment:
        if len(set(self.factors)) != len(self.factors):
            raise ValueError("risk complexity factors must be unique")
        if len(set(self.objective_order)) != len(self.objective_order):
            raise ValueError("risk complexity objective_order must not contain duplicates")
        if len(set(self.required_roles)) != len(self.required_roles):
            raise ValueError("risk complexity required_roles must not contain duplicates")
        return self


def default_risk_complexity_policy() -> RiskComplexityPolicy:
    """Return the versioned MVP policy used by compatibility-created policies."""
    effect = RiskComplexityEffect
    return RiskComplexityPolicy(
        policy_version="risk-complexity/v1",
        risk_overrides={
            "sensitive": "complex",
            "external_mutation": "critical",
            "destructive": "critical",
            "irreversible": "critical",
        },
        ordered_rules=(
            RiskComplexityRule(
                rule_id="missing-required-evidence",
                when="required_evidence_unavailable",
                complexity="critical",
            ),
            RiskComplexityRule(
                rule_id="missing-required-expertise",
                when="required_expertise_unavailable",
                complexity="complex",
            ),
            RiskComplexityRule(rule_id="large-task", when="size_is_L", complexity="complex"),
            RiskComplexityRule(rule_id="medium-task", when="size_is_M", complexity="moderate"),
            RiskComplexityRule(
                rule_id="dependencies-present",
                when="dependencies_present",
                complexity="moderate",
            ),
            RiskComplexityRule(
                rule_id="expected-proofs-present",
                when="expected_proofs_present",
                complexity="moderate",
            ),
            RiskComplexityRule(
                rule_id="verification-strategy",
                when="strategy_requires_verification",
                complexity="moderate",
            ),
        ),
        effects={
            "simple": effect(
                objective_order=("efficiency", "quality"),
                verification_depth="standard",
            ),
            "moderate": effect(
                objective_order=("quality", "efficiency"),
                verification_depth="elevated",
                required_roles=("reviewer",),
            ),
            "complex": effect(
                objective_order=("quality", "efficiency"),
                verification_depth="strict",
                required_roles=("reviewer", "critic"),
            ),
            "critical": effect(
                objective_order=("quality",),
                verification_depth="strict",
                required_roles=("reviewer", "critic", "referee"),
            ),
        },
    )


__all__ = [
    "ComplexityLevel",
    "ReviewRole",
    "RiskComplexityAssessment",
    "RiskComplexityEffect",
    "RiskComplexityPolicy",
    "RiskComplexityPredicate",
    "RiskComplexityRule",
    "VerificationDepth",
    "default_risk_complexity_policy",
]
