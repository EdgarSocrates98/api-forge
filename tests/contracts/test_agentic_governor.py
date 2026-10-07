"""§23-§27 contracts: governor, gain, stop, recovery, loop detection."""

from __future__ import annotations

from apiforge.contracts.agentic_governance import (
    ExpectedInformationGain,
    GovernorDecision,
    GovernorInputs,
    LoopDetection,
    RecoveryDecision,
    StopDecision,
)


def test_governor_inputs_optional_signals() -> None:
    inputs = GovernorInputs(profile="economy", risk="read_only")
    assert inputs.confidence is None
    assert inputs.security_state == "clean"


def test_governor_decision_shape() -> None:
    decision = GovernorDecision(
        profile="balanced",
        risk="sensitive",
        max_agents=2,
        max_reviewers=1,
        max_debates=1,
        max_retries=2,
        max_replans=1,
        allowed_execution_modes=("deterministic", "sandbox"),
        allowed_tools=("read_only",),
        clamped_by=("security:tainted",),
        unresolved=("confidence",),
    )
    assert decision.max_cost is None
    assert "confidence" in decision.unresolved


def test_expected_information_gain_unresolved_level() -> None:
    gain = ExpectedInformationGain(
        action="start_debate",
        score=None,
        level="unresolved",
        signals={},
        reason="no measurable signal",
        unresolved=("agreement",),
    )
    assert gain.score is None


def test_stop_decision_carries_code() -> None:
    stop = StopDecision(
        decision="stop",
        expected_gain=0.1,
        threshold=0.33,
        code="AF-GOV-STOP-LOW-GAIN",
    )
    assert stop.mandatory_requirement is False


def test_recovery_decision_terminal() -> None:
    decision = RecoveryDecision(
        failure_class="budget_exhausted",
        decision="stop",
        attempt=3,
        max_attempts=0,
        code="AF-GOV-RECOVERY-EXHAUSTED",
    )
    assert decision.decision == "stop"


def test_loop_detection_blocked() -> None:
    detection = LoopDetection(
        strategy_fingerprint="strategy:abc",
        repeats=2,
        window=5,
        blocked=True,
        code="AF-GOV-LOOP-DETECTED",
    )
    assert detection.blocked
    assert detection.action == "stop"
