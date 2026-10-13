"""§23 Agent Governor: ceilings by profile, risk floor, security and budget."""

from __future__ import annotations

from apiforge.contracts.agentic_governance import GovernorInputs
from apiforge.governance.governor import govern, load_governor_policy


def test_economy_profile_ceilings() -> None:
    decision = govern(GovernorInputs(profile="economy", risk="read_only"))
    assert decision.max_agents == 1
    assert decision.max_reviewers == 0
    assert decision.allowed_execution_modes == ("deterministic",)


def test_risk_floor_raises_profile() -> None:
    decision = govern(GovernorInputs(profile="economy", risk="irreversible"))
    assert decision.profile == "deep"
    assert "risk:irreversible->deep" in decision.clamped_by
    assert decision.max_reviewers == 2


def test_floor_never_lowers_profile() -> None:
    decision = govern(GovernorInputs(profile="deep", risk="read_only"))
    assert decision.profile == "deep"
    assert not any(c.startswith("risk:") for c in decision.clamped_by)


def test_security_clamp_restricts_tools() -> None:
    decision = govern(
        GovernorInputs(profile="deep", risk="local_reversible", security_state="tainted")
    )
    assert "provider" not in decision.allowed_execution_modes
    assert decision.allowed_tools == ("read_only",)
    assert "security:tainted" in decision.clamped_by


def test_quarantined_is_deterministic_only() -> None:
    decision = govern(
        GovernorInputs(profile="deep", risk="read_only", security_state="quarantined")
    )
    assert decision.allowed_execution_modes == ("deterministic",)


def test_budget_remaining_clamps_tokens_and_calls() -> None:
    decision = govern(
        GovernorInputs(
            profile="deep",
            risk="read_only",
            budget_remaining={"observed_tokens": 500, "cost": 0.5, "calls": 3},
        )
    )
    assert decision.max_tokens == 500
    assert decision.max_cost == 0.5
    assert decision.max_agents + decision.max_reviewers <= 3
    assert "budget:observed_tokens" in decision.clamped_by
    assert "budget:calls" in decision.clamped_by


def test_missing_inputs_named_unresolved() -> None:
    decision = govern(GovernorInputs(profile="balanced", risk="sensitive"))
    assert set(decision.unresolved) == {
        "confidence",
        "evidence_completeness",
        "context_sufficiency",
        "task_complexity",
    }


def test_declared_inputs_not_unresolved() -> None:
    decision = govern(
        GovernorInputs(
            profile="balanced",
            risk="sensitive",
            confidence=0.8,
            evidence_completeness=0.9,
            context_sufficiency=0.7,
            task_complexity="medium",
        )
    )
    assert decision.unresolved == ()


def test_policy_loads_declared_yaml() -> None:
    policy = load_governor_policy()
    assert policy["schema"] == "apiforge/governor-policy/v1"
    assert "deep" in policy["profiles"]
