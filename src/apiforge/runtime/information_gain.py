"""Expected information gain of one more agent after L2 (§80).

``low`` when every artifact agrees, nothing is unresolved and confidence is
at or above the escalation threshold — another agent would most likely
restate what is known, so the run stops. ``high`` on disagreement or
unresolved items; ``medium`` otherwise. The level explains the existing
escalation triggers; it never overrides a risk-required role.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from apiforge.contracts.economy_evals import InformationGain


def assess(artifacts: Sequence[Any], threshold: float = 0.7) -> InformationGain:
    if not artifacts:
        return InformationGain(level="high", reason="no artifact produced yet")
    recommendations = {str((item.payload or {}).get("recommendation", "")) for item in artifacts}
    unresolved = sorted({gap for item in artifacts for gap in item.unresolved})
    confidences = [item.confidence for item in artifacts if item.confidence is not None]
    lowest = min(confidences) if confidences else None
    if len(recommendations) > 1:
        return InformationGain(level="high", reason="artifacts disagree on the recommendation")
    if unresolved:
        return InformationGain(level="high", reason=f"{len(unresolved)} unresolved item(s)")
    if lowest is None or lowest < threshold:
        return InformationGain(level="medium", reason="confidence below the escalation threshold")
    return InformationGain(
        level="low", reason="artifacts agree, nothing unresolved, confidence at threshold or above"
    )


__all__ = ["assess"]
