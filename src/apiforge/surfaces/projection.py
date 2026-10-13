"""Shared capability projection used by every host surface."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from apiforge.contracts.platform import (
    CapabilityRecord,
    CapabilityRequest,
    CapabilityResult,
    ResultStatus,
)
from apiforge.core.models import JsonValue


def project_capability(
    request: CapabilityRequest,
    records: Sequence[CapabilityRecord],
    *,
    payload: Mapping[str, JsonValue] | None = None,
) -> CapabilityResult:
    """Project one capability without changing its support semantics."""
    record = next((item for item in records if item.capability_id == request.capability_id), None)
    if record is None:
        return CapabilityResult(
            capability_id=request.capability_id,
            state="unsupported",
            status="blocked",
            error_code="AF-CAPABILITY-NOT-FOUND",
            gaps=("capability is not registered",),
        )
    status: ResultStatus = "ok" if record.state == "supported" else "review"
    if request.action == "apply" and record.risk == "external_mutation":
        status = "blocked"
    return CapabilityResult(
        capability_id=record.capability_id,
        state=record.state,
        status=status,
        payload=payload or {},
        evidence=record.evidence,
        limitations=record.limitations,
        gaps=("external mutation requires an integration approval gate",)
        if status == "blocked"
        else (),
        error_code="AF-SURFACE-MUTATION-GATE" if status == "blocked" else None,
    )
