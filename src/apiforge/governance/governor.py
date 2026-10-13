"""§23 Agent Governor: profile ceilings adjusted by risk, security and budget.

The effective profile is ``max(declared profile, risk floor)`` — a cheaper
profile is never used below the risk floor. Security-state clamps restrict
execution modes and tools; declared ``budget_remaining`` clamps the numeric
ceilings. Missing inputs are named in ``unresolved``, never guessed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.agentic_governance import (
    GovernorDecision,
    GovernorInputs,
    GovernorProfile,
)

GOVERNOR_POLICY = Path(__file__).resolve().parent.parent / "rules" / "governor_policy.yaml"

_ORDER: tuple[GovernorProfile, ...] = ("economy", "balanced", "deep")

# budget_remaining keys -> the ceiling they clamp.
_BUDGET_CLAMPS: tuple[tuple[str, str], ...] = (
    ("observed_tokens", "max_tokens"),
    ("calls", "_calls"),
)


def load_governor_policy(path: Path = GOVERNOR_POLICY) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "apiforge/governor-policy/v1":
        raise ValueError(f"{path} is not an apiforge/governor-policy/v1 file")
    return data


def _raised(a: GovernorProfile, b: str) -> GovernorProfile:
    """Max of two profiles in the declared order."""
    try:
        return _ORDER[max(_ORDER.index(a), _ORDER.index(b))]
    except ValueError:
        return a


def govern(inputs: GovernorInputs, policy: dict[str, Any] | None = None) -> GovernorDecision:
    """Resolve the §23 ceilings for one run; every clamp is named."""
    policy = policy if policy is not None else load_governor_policy()
    profiles = policy.get("profiles") or {}
    floors = policy.get("risk_floors") or {}
    clamps: list[str] = []
    unresolved: list[str] = []

    effective = _raised(inputs.profile, str(floors.get(inputs.risk, inputs.profile)))
    if effective != inputs.profile:
        clamps.append(f"risk:{inputs.risk}->{effective}")
    row = dict(profiles.get(effective) or {})

    security = (policy.get("security_clamps") or {}).get(inputs.security_state)
    modes: list[str] = list(row.get("allowed_execution_modes") or [])
    tools: list[str] = list(row.get("allowed_tools") or [])
    if security:
        modes = [m for m in modes if m in (security.get("allowed_execution_modes") or modes)]
        tools = [t for t in tools if t in (security.get("allowed_tools") or tools)]
        clamps.append(f"security:{inputs.security_state}")

    max_tokens = row.get("max_tokens")
    max_cost = row.get("max_cost")
    max_agents = int(row.get("max_agents", 0))
    max_reviewers = int(row.get("max_reviewers", 0))
    remaining = inputs.budget_remaining
    tokens_left = remaining.get("observed_tokens")
    if tokens_left is not None:
        max_tokens = tokens_left if max_tokens is None else min(max_tokens, tokens_left)
        clamps.append("budget:observed_tokens")
    cost_left = remaining.get("cost")
    if cost_left is not None:
        max_cost = float(cost_left) if max_cost is None else min(max_cost, float(cost_left))
        clamps.append("budget:cost")
    calls_left = remaining.get("calls")
    if calls_left is not None and max_agents + max_reviewers > calls_left:
        left = int(calls_left)
        max_agents = min(max_agents, left)
        max_reviewers = min(max_reviewers, max(0, left - max_agents))
        clamps.append("budget:calls")

    for name in ("confidence", "evidence_completeness", "context_sufficiency"):
        if getattr(inputs, name) is None:
            unresolved.append(name)
    if inputs.task_complexity is None:
        unresolved.append("task_complexity")

    return GovernorDecision(
        profile=effective,
        risk=inputs.risk,
        max_agents=max_agents,
        max_reviewers=max_reviewers,
        max_debates=int(row.get("max_debates", 0)),
        max_retries=int(row.get("max_retries", 0)),
        max_replans=int(row.get("max_replans", 0)),
        max_tokens=max_tokens,
        max_cost=max_cost,
        allowed_execution_modes=tuple(modes),  # type: ignore[arg-type]
        allowed_tools=tuple(tools),
        clamped_by=tuple(sorted(set(clamps))),
        unresolved=tuple(sorted(unresolved)),
    )


__all__ = ["GOVERNOR_POLICY", "govern", "load_governor_policy"]
