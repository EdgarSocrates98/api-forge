"""§27 Loop Detection: repeated strategy fingerprints get blocked."""

from __future__ import annotations

from apiforge.governance.loop import check_loop, strategy_fingerprint


def test_fingerprint_canonical() -> None:
    a = strategy_fingerprint({"steps": ["x", "y"], "tool": "t"})
    b = strategy_fingerprint({"tool": "t", "steps": ["x", "y"]})
    assert a == b


def test_distinct_strategies_distinct_fingerprints() -> None:
    a = strategy_fingerprint({"steps": ["x"]})
    b = strategy_fingerprint({"steps": ["z"]})
    assert a != b


def test_repeated_strategy_blocks() -> None:
    fp = strategy_fingerprint({"plan": "same"})
    result = check_loop([fp, "other", fp, fp], window=5, max_repeats=2)
    assert result.blocked
    assert result.code == "AF-GOV-LOOP-DETECTED"
    assert result.repeats == 2


def test_single_repeat_allowed() -> None:
    fp = strategy_fingerprint({"plan": "same"})
    result = check_loop([fp, fp], window=5, max_repeats=2)
    assert not result.blocked
    assert result.repeats == 1


def test_window_bounds_repeats() -> None:
    fp = strategy_fingerprint({"plan": "same"})
    # old repeats fall outside the window
    history = [fp, fp, fp, "other-a", "other-b", "other-c", "other-d", fp]
    result = check_loop(history, window=4, max_repeats=2)
    assert not result.blocked


def test_empty_history_never_blocks() -> None:
    result = check_loop([])
    assert not result.blocked
    assert result.repeats == 0
