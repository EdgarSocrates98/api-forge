"""§24 Expected Information Gain v2: a pre-action scored signal bundle.

Before spawning an agent, calling a reviewer, starting a debate, expanding
context or performing expensive retrieval, the caller supplies the §24
signals each normalized to ``0..1`` where higher means *more* expected
gain. Coverage/agreement/confidence inputs are inverted into gap terms so
one weighted mean answers "how much could this action still add".

Missing signals are dropped from the mean and named in ``unresolved`` —
the score never silently treats an unmeasured signal as zero.
"""

from __future__ import annotations

from apiforge.contracts.agentic_governance import ExpectedInformationGain, GainAction

# caller input -> gain term (higher = more expected gain)
_INVERTED = {"agreement", "evidence_coverage", "confidence", "role_coverage", "context_coverage"}
_WEIGHTS: dict[str, float] = {
    "agreement": 0.15,  # inverted: disagreement drives gain
    "unresolved_share": 0.20,
    "evidence_coverage": 0.20,  # inverted: evidence gap drives gain
    "confidence": 0.10,  # inverted
    "novelty_potential": 0.15,
    "remaining_budget": 0.05,
    "role_coverage": 0.10,  # inverted
    "context_coverage": 0.05,  # inverted
}

_LEVELS = ((0.66, "high"), (0.33, "medium"), (0.0, "low"))


def expected_gain(
    action: GainAction,
    signals: dict[str, float | None],
) -> ExpectedInformationGain:
    """Score the expected information gain of ``action`` over the signals."""
    terms: dict[str, float | None] = {}
    unresolved: list[str] = []
    weighted = 0.0
    weight = 0.0
    for name, w in _WEIGHTS.items():
        raw = signals.get(name)
        if raw is None:
            terms[name] = None
            unresolved.append(name)
            continue
        value = min(1.0, max(0.0, float(raw)))
        term = 1.0 - value if name in _INVERTED else value
        terms[name] = round(term, 4)
        weighted += term * w
        weight += w
    if weight == 0.0:
        return ExpectedInformationGain(
            action=action,
            score=None,
            level="unresolved",
            signals=terms,
            reason="no measurable signal supplied",
            unresolved=tuple(sorted(unresolved)),
        )
    score = round(weighted / weight, 4)
    level = next(label for floor, label in _LEVELS if score >= floor)
    return ExpectedInformationGain(
        action=action,
        score=score,
        level=level,  # type: ignore[arg-type]
        signals=terms,
        reason=f"{action}: weighted gain {score} over {len(unresolved)} unresolved signal(s)",
        unresolved=tuple(sorted(unresolved)),
    )


__all__ = ["expected_gain"]
