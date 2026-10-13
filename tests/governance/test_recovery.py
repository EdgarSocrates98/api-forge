"""§26 Recovery Governance: declared ladders, terminal actions, undeclared."""

from __future__ import annotations

from apiforge.governance.recovery import decide_recovery, load_recovery_policy


def test_first_attempt_uses_first_run() -> None:
    decision = decide_recovery("timeout", 0)
    assert decision.decision == "retry"
    assert decision.max_attempts == 2


def test_second_attempt_moves_down_ladder() -> None:
    decision = decide_recovery("provider_failure", 1)
    assert decision.decision == "fallback"


def test_exhausted_attempts_fire_terminal() -> None:
    decision = decide_recovery("provider_failure", 3)
    assert decision.decision == "escalate"
    assert decision.code == "AF-GOV-RECOVERY-EXHAUSTED"


def test_terminal_actions_are_never_retry() -> None:
    for failure_class in load_recovery_policy()["classes"]:
        decision = decide_recovery(failure_class, 99)
        assert decision.decision in {"escalate", "stop"}


def test_budget_exhausted_stops_immediately() -> None:
    decision = decide_recovery("budget_exhausted", 0)
    assert decision.decision == "stop"


def test_unknown_failure_class_refuses() -> None:
    import pytest

    from apiforge.economy.run_ledger import EconomyError

    with pytest.raises(EconomyError, match="AF-GOV-FAILURE-CLASS-UNKNOWN"):
        decide_recovery("ghost_failure", 0)


def test_class_absent_from_policy_escalates_named() -> None:
    decision = decide_recovery("timeout", 0, {"classes": {}})
    assert decision.decision == "escalate"
    assert decision.code == "AF-GOV-RECOVERY-UNDECLARED"
    assert "timeout" in decision.unresolved


def test_every_declared_class_walks() -> None:
    policy = load_recovery_policy()
    for failure_class, row in policy["classes"].items():
        for attempt in range(int(row["max_attempts"]) + 1):
            decision = decide_recovery(failure_class, attempt)
            assert decision.failure_class == failure_class
