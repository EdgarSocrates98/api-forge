"""Correlate telemetry, SLOs and performance evidence into an agent-safe health view."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.observability import SLOResult, TelemetryRecord
from apiforge.observability.signals import summarize


class HealthAssessment(VersionedContract):
    service: str
    status: Literal["healthy", "degraded", "incident", "inconclusive"]
    severity: Literal["info", "warning", "critical"]
    request_count: int = Field(ge=0)
    error_rate: float | None = Field(default=None, ge=0, le=1)
    slo_statuses: tuple[str, ...] = ()
    performance_verdicts: tuple[str, ...] = ()
    signals: tuple[str, ...] = ()
    recommended_actions: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


def assess_health(
    service: str,
    records: tuple[TelemetryRecord, ...],
    slo_results: tuple[SLOResult, ...] = (),
    performance_verdicts: tuple[str, ...] = (),
) -> HealthAssessment:
    """Produce a bounded assessment; missing telemetry is explicitly inconclusive."""
    summaries = summarize(records)
    request_count = sum(item.request_count for item in summaries)
    errors = sum(item.error_count for item in summaries)
    error_rate = errors / request_count if request_count else None
    slo_statuses = tuple(item.status for item in slo_results)
    signals: list[str] = []
    actions: list[str] = []
    gaps: list[str] = []
    if not records:
        gaps.append("no telemetry records for service")
    if error_rate is not None and error_rate > 0:
        signals.append(f"error_rate={error_rate:.4f}")
        actions.append("inspect correlated traces and downstream error boundaries")
    if "breached" in slo_statuses:
        signals.append("one or more SLOs breached")
        actions.append("open incident using the owning service runbook")
    if any(item == "FAIL" for item in performance_verdicts):
        signals.append("performance assessment failed")
        actions.append("compare against baseline before changing capacity")
    if gaps:
        status: Literal["healthy", "degraded", "incident", "inconclusive"] = "inconclusive"
        severity: Literal["info", "warning", "critical"] = "warning"
    elif "breached" in slo_statuses or "FAIL" in performance_verdicts:
        status, severity = "incident", "critical"
    elif signals:
        status, severity = "degraded", "warning"
    else:
        status, severity = "healthy", "info"
    return HealthAssessment(
        service=service,
        status=status,
        severity=severity,
        request_count=request_count,
        error_rate=error_rate,
        slo_statuses=slo_statuses,
        performance_verdicts=performance_verdicts,
        signals=tuple(signals),
        recommended_actions=tuple(actions),
        gaps=tuple(gaps),
        evidence=tuple(sorted({record.source for record in records})),
    )
