"""Pure policy decision: rules first-match, then the class default.

The engine never self-satisfies a gate — a `gate` outcome only becomes
`allow` when the caller supplies every required field in ``detail``, and the
decision records which fields satisfied it.
"""

from __future__ import annotations

import fnmatch
from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field

from apiforge.policy.models import AutonomyClass, Policy


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ActionRequest(_Frozen):
    """A described action, before it runs."""

    verb: str
    autonomy_class: str | None = None
    args: tuple[str, ...] = ()
    target: str | None = None
    detail: Mapping[str, str] = Field(default_factory=dict)


class PolicyDecision(_Frozen):
    outcome: str  # allow | gate | deny
    rule: str | None = None
    reason_code: str | None = None
    missing_requirements: tuple[str, ...] = ()
    satisfied_by: tuple[str, ...] = ()
    subject: str


def _rule_matches(verb_pat: str, arg_glob: str | None, action: ActionRequest) -> bool:
    if not fnmatch.fnmatchcase(action.verb, verb_pat):
        return False
    if arg_glob is None:
        return True
    return any(fnmatch.fnmatchcase(arg, arg_glob) for arg in action.args)


def decide(policy: Policy, action: ActionRequest) -> PolicyDecision:
    """Evaluate ``action`` against ``policy`` — pure, deterministic."""
    subject = action.verb if action.target is None else f"{action.verb} {action.target}"

    for rule in policy.rules:
        if _rule_matches(rule.match.verb, rule.match.arg_glob, action):
            return _outcome(policy, rule.decision, action, subject, rule.name, rule.reason)

    try:
        klass = AutonomyClass(action.autonomy_class) if action.autonomy_class else None
    except ValueError:
        klass = None
    if klass is None:
        return PolicyDecision(
            outcome="deny",
            reason_code="AF-POLICY-CLASS-UNKNOWN",
            subject=subject,
        )
    return _outcome(policy, policy.defaults[klass], action, subject, None, None, klass)


def _outcome(
    policy: Policy,
    decision: str,
    action: ActionRequest,
    subject: str,
    rule: str | None,
    reason: str | None,
    klass: AutonomyClass | None = None,
) -> PolicyDecision:
    if decision == "allow":
        return PolicyDecision(outcome="allow", rule=rule, subject=subject)
    if decision == "deny":
        return PolicyDecision(
            outcome="deny",
            rule=rule,
            reason_code=reason or "AF-POLICY-DENY",
            subject=subject,
        )
    # gate
    gate_class = klass
    if gate_class is None:
        try:
            gate_class = AutonomyClass(action.autonomy_class) if action.autonomy_class else None
        except ValueError:
            gate_class = None
    requirements = tuple(policy.gates.get(gate_class, ())) if gate_class else ()
    satisfied = tuple(r for r in requirements if action.detail.get(r))
    missing = tuple(r for r in requirements if r not in satisfied)
    if missing:
        return PolicyDecision(
            outcome="gate",
            rule=rule,
            reason_code="AF-POLICY-GATE",
            missing_requirements=missing,
            satisfied_by=satisfied,
            subject=subject,
        )
    return PolicyDecision(outcome="allow", rule=rule, satisfied_by=satisfied, subject=subject)
