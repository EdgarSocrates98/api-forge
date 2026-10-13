"""§25 Agent Stop Policy: continue on expected gain or requirement only.

The system does not continue merely because budget remains: it continues
when ``expected_gain > threshold`` or a mandatory requirement is still
unmet. An unmeasurable gain fails closed — STOP with
``AF-GOV-GAIN-UNRESOLVED`` — because continuing cannot be justified.
"""

from __future__ import annotations

from apiforge.contracts.agentic_governance import ExpectedInformationGain, StopDecision


def decide_stop(
    gain: ExpectedInformationGain,
    *,
    mandatory_requirement: bool = False,
    threshold: float = 0.33,
) -> StopDecision:
    """Resolve continue/stop; gain strictly above the threshold continues."""
    if mandatory_requirement:
        return StopDecision(
            decision="continue",
            expected_gain=gain.score,
            threshold=threshold,
            mandatory_requirement=True,
            reason="mandatory requirement unmet; run continues regardless of gain",
        )
    if gain.score is None:
        return StopDecision(
            decision="stop",
            expected_gain=None,
            threshold=threshold,
            reason="expected gain is unmeasurable; continuing is not justified",
            code="AF-GOV-GAIN-UNRESOLVED",
        )
    if gain.score > threshold:
        return StopDecision(
            decision="continue",
            expected_gain=gain.score,
            threshold=threshold,
            reason=f"expected gain {gain.score} above threshold {threshold}",
        )
    return StopDecision(
        decision="stop",
        expected_gain=gain.score,
        threshold=threshold,
        reason=f"expected gain {gain.score} at or below threshold {threshold}",
        code="AF-GOV-STOP-LOW-GAIN",
    )


__all__ = ["decide_stop"]
