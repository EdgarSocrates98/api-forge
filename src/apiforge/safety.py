"""Explicit API security and resilience gate."""

from __future__ import annotations

from collections.abc import Mapping

from apiforge.contracts.stubs import ApiSafetyAssessment

REQUIRED_API_CONTROLS = (
    "authentication",
    "authorization",
    "input_validation",
    "idempotency",
    "timeout",
    "retry_policy",
    "circuit_breaker",
    "rate_limit",
    "structured_observability",
)


def assess_api_safety(
    subject: str,
    controls: Mapping[str, bool | None],
) -> ApiSafetyAssessment:
    """Assess declared controls; ``None`` is review, never an implicit pass."""

    passed = tuple(name for name in REQUIRED_API_CONTROLS if controls.get(name) is True)
    missing = tuple(name for name in REQUIRED_API_CONTROLS if controls.get(name) is None)
    failed = tuple(name for name in REQUIRED_API_CONTROLS if controls.get(name) is False)
    status = "blocked" if failed else ("review" if missing else "ready")
    return ApiSafetyAssessment(
        id=f"safety-{subject}",
        subject=subject,
        status=status,  # type: ignore[arg-type]
        required_controls=REQUIRED_API_CONTROLS,
        passed_controls=passed,
        missing_controls=missing,
        failed_controls=failed,
        evidence=("declared-controls", "no-network-called"),
    )
