"""§24 Expected Information Gain v2: weighted signals, honest gaps."""

from __future__ import annotations

from apiforge.governance.gain import expected_gain

_FULL = {
    "agreement": 0.9,  # low disagreement -> low gain
    "unresolved_share": 0.0,
    "evidence_coverage": 1.0,  # full coverage -> no gap
    "confidence": 0.9,
    "novelty_potential": 0.0,
    "remaining_budget": 1.0,
    "role_coverage": 1.0,
    "context_coverage": 1.0,
}


def test_full_agreement_is_low_gain() -> None:
    gain = expected_gain("start_debate", dict(_FULL))
    assert gain.level == "low"
    assert gain.unresolved == ()


def test_disagreement_and_gaps_raise_gain() -> None:
    signals = dict(_FULL)
    signals.update(
        {
            "agreement": 0.0,
            "unresolved_share": 0.9,
            "evidence_coverage": 0.2,
            "confidence": 0.3,
            "novelty_potential": 0.8,
            "context_coverage": 0.2,
        }
    )
    gain = expected_gain("start_debate", signals)
    assert gain.level == "high"
    assert gain.score is not None and gain.score > 0.66


def test_missing_signals_dropped_and_named() -> None:
    gain = expected_gain("spawn_agent", {"unresolved_share": 0.5})
    assert gain.score is not None
    assert "agreement" in gain.unresolved
    assert "novelty_potential" in gain.unresolved
    # score is a mean over the single present signal
    assert gain.score == 0.5


def test_no_signals_is_unresolved() -> None:
    gain = expected_gain("expand_context", {})
    assert gain.score is None
    assert gain.level == "unresolved"


def test_signals_clamped_to_unit() -> None:
    gain = expected_gain("call_reviewer", {"unresolved_share": 4.0})
    assert gain.signals["unresolved_share"] == 1.0
    assert gain.score == 1.0


def test_inverted_semantics() -> None:
    # full evidence coverage must produce zero evidence-gap term
    gain = expected_gain("expensive_retrieval", {"evidence_coverage": 1.0})
    assert gain.signals["evidence_coverage"] == 0.0
    gain = expected_gain("expensive_retrieval", {"evidence_coverage": 0.0})
    assert gain.signals["evidence_coverage"] == 1.0
