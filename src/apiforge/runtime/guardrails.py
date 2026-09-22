"""Deterministic validation of specialist agent output."""

from __future__ import annotations

from apiforge.core.models import JsonValue


def validate_agent_payload(payload: dict[str, JsonValue]) -> tuple[str, ...]:
    """Return contract gaps that prevent a structured recommendation."""
    gaps: list[str] = []
    recommendation = payload.get("recommendation")
    if not isinstance(recommendation, str) or not recommendation.strip():
        gaps.append("agent output requires a non-empty recommendation")
    for key in ("facts", "assumptions", "risks", "unresolved"):
        value = payload.get(key, ())
        if not isinstance(value, (list, tuple)):
            gaps.append(f"agent output field {key!r} must be a list")
    confidence = payload.get("confidence")
    if confidence is not None and not isinstance(confidence, (int, float)):
        gaps.append("agent output confidence must be numeric")
    if isinstance(confidence, (int, float)) and not 0 <= confidence <= 1:
        gaps.append("agent output confidence must be between zero and one")
    return tuple(sorted(set(gaps)))
