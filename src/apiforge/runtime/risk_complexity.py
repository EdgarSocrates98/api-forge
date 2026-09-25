"""Pure deterministic classification of task risk and complexity."""

from __future__ import annotations

from typing import TYPE_CHECKING

from apiforge.contracts.risk_complexity import (
    ComplexityLevel,
    RiskComplexityAssessment,
    RiskComplexityGate,
    RiskComplexityRule,
)
from apiforge.core.ids import stable_id

if TYPE_CHECKING:
    from apiforge.contracts.routing import RoutingPolicy, RoutingRequest


_RISK_LEVELS: dict[str, int] = {
    "simple": 0,
    "moderate": 1,
    "complex": 2,
    "critical": 3,
}
_SUPPORTED_RISKS = {
    "read_only",
    "local_reversible",
    "sensitive",
    "external_mutation",
    "destructive",
    "irreversible",
}
_VERIFICATION_STRATEGIES = {
    "plan-execute-verify",
    "diagnose-repair-verify",
    "research-synthesize-verify",
    "verified-api-slice",
    "test-first",
}


def _rule_matches(rule: RiskComplexityRule, request: RoutingRequest) -> bool:
    missing_evidence = set(request.required_evidence).difference(request.available_evidence)
    missing_expertise = set(request.required_expertise).difference(request.available_expertise)
    if rule.when == "required_evidence_unavailable":
        return bool(missing_evidence)
    if rule.when == "required_expertise_unavailable":
        return bool(missing_expertise)
    if rule.when == "size_is_L":
        return request.task_size == "L"
    if rule.when == "size_is_M":
        return request.task_size == "M"
    if rule.when == "dependencies_present":
        return bool(request.dependencies)
    if rule.when == "expected_proofs_present":
        return bool(request.expected_proofs)
    if rule.when == "strategy_requires_verification":
        return request.strategy in _VERIFICATION_STRATEGIES
    return False


def _promote(current: ComplexityLevel, candidate: ComplexityLevel) -> ComplexityLevel:
    return candidate if _RISK_LEVELS[candidate] > _RISK_LEVELS[current] else current


def _ordered_unique(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _unresolved_inputs(request: RoutingRequest) -> tuple[str, ...]:
    unresolved: list[str] = []
    missing_evidence = tuple(sorted(set(request.required_evidence).difference(request.available_evidence)))
    if missing_evidence:
        unresolved.append(
            "AF-CAPABILITY-ELIGIBILITY: field=required_evidence; "
            "unlock=provide the missing evidence before routing; "
            f"missing={','.join(missing_evidence)}"
        )
    missing_expertise = tuple(
        sorted(set(request.required_expertise).difference(request.available_expertise))
    )
    if missing_expertise:
        unresolved.append(
            "AF-CAPABILITY-ELIGIBILITY: field=required_expertise; "
            "unlock=make the validated local expertise pack available before routing; "
            f"missing={','.join(missing_expertise)}"
        )
    if request.risk not in _SUPPORTED_RISKS:
        unresolved.append(
            "AF-CAPABILITY-ELIGIBILITY: field=risk; "
            "unlock=provide a supported TaskRisk value"
        )
    return tuple(unresolved)


def assess_risk_complexity(
    request: RoutingRequest,
    policy: RoutingPolicy,
) -> RiskComplexityAssessment:
    """Classify explicit local inputs without time, network or provider state."""
    complexity: ComplexityLevel = "simple"
    factors: list[str] = []
    override = policy.risk_complexity.risk_overrides.get(request.risk)
    if override is not None:
        complexity = _promote(complexity, override)
        factors.append(f"risk:{request.risk}")
    for rule in policy.risk_complexity.ordered_rules:
        if _rule_matches(rule, request):
            complexity = _promote(complexity, rule.complexity)
            factors.append(f"rule:{rule.rule_id}")
    unresolved = _unresolved_inputs(request)
    effect = policy.risk_complexity.effects.get(complexity)
    if effect is None:
        unresolved = (*unresolved, "AF-RUNTIME-POLICY: field=risk_complexity.effects; unlock=define the selected complexity effect")
        effect = policy.risk_complexity.effects["critical"]
    gate_state: RiskComplexityGate = (
        "blocked" if unresolved else "review" if complexity != "simple" else "open"
    )
    evidence = tuple(sorted(set(request.available_evidence)))
    assessment_id = stable_id(
        "risk-assessment",
        {
            "task_id": request.task_id,
            "revision": request.revision,
            "policy_id": policy.policy_id,
            "policy_version": policy.risk_complexity.policy_version,
            "risk": request.risk,
            "task_size": request.task_size,
            "dependencies": request.dependencies,
            "expected_proofs": request.expected_proofs,
            "strategy": request.strategy,
            "required_evidence": request.required_evidence,
            "available_evidence": request.available_evidence,
            "required_expertise": request.required_expertise,
            "available_expertise": request.available_expertise,
            "factors": _ordered_unique(factors),
            "unresolved": unresolved,
        },
    )
    return RiskComplexityAssessment(
        assessment_id=assessment_id,
        task_id=request.task_id,
        revision=request.revision,
        policy_id=policy.policy_id,
        policy_version=policy.risk_complexity.policy_version,
        risk=request.risk,
        complexity=complexity,
        factors=_ordered_unique(factors),
        objective_order=effect.objective_order,
        verification_depth=effect.verification_depth,
        required_roles=effect.required_roles,
        gate_state=gate_state,
        evidence=evidence,
        unresolved=unresolved,
    )


__all__ = ["assess_risk_complexity"]
