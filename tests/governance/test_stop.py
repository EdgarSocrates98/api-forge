"""§25 Stop Policy: explicit STOP when gain cannot justify continuing."""

from __future__ import annotations

from apiforge.governance.gain import expected_gain
from apiforge.governance.stop import decide_stop


def test_continue_above_threshold() -> None:
    gain = expected_gain("start_debate", {"unresolved_share": 0.9})
    decision = decide_stop(gain, threshold=0.33)
    assert decision.decision == "continue"
    assert decision.code is None


def test_stop_at_or_below_threshold() -> None:
    gain = expected_gain("call_reviewer", {"unresolved_share": 0.1})
    decision = decide_stop(gain, threshold=0.33)
    assert decision.decision == "stop"
    assert decision.code == "AF-GOV-STOP-LOW-GAIN"


def test_mandatory_requirement_continues() -> None:
    gain = expected_gain("call_reviewer", {"unresolved_share": 0.0})
    decision = decide_stop(gain, mandatory_requirement=True, threshold=0.33)
    assert decision.decision == "continue"
    assert decision.mandatory_requirement


def test_unmeasurable_gain_stops_fail_closed() -> None:
    gain = expected_gain("spawn_agent", {})
    decision = decide_stop(gain)
    assert decision.decision == "stop"
    assert decision.code == "AF-GOV-GAIN-UNRESOLVED"


def test_boundary_is_strict() -> None:
    # exactly-at-threshold does not continue
    gain = expected_gain("expand_context", {"unresolved_share": 0.33})
    decision = decide_stop(gain, threshold=0.33)
    assert decision.decision == "stop"
