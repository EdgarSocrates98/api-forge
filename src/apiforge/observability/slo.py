"""SLO and error-budget evaluation with explicit inconclusive state."""

from __future__ import annotations

from collections.abc import Iterable

from apiforge.contracts.observability import SLODefinition, SLOResult, TelemetryRecord


def evaluate_slo(definition: SLODefinition, records: Iterable[TelemetryRecord]) -> SLOResult:
    selected = [record for record in records if record.service == definition.service]
    if definition.indicator == "latency":
        good = [
            record
            for record in selected
            if record.duration_ms is not None
            and definition.threshold_ms is not None
            and record.duration_ms <= definition.threshold_ms
        ]
    else:
        good = [
            record
            for record in selected
            if record.status_code is not None and record.status_code < 500
        ]
    total = len(selected)
    if (
        not total
        or not good
        and definition.indicator == "latency"
        and definition.threshold_ms is None
    ):
        return SLOResult(
            slo_id=definition.id,
            status="inconclusive",
            good_events=len(good),
            total_events=total,
            objective=definition.objective,
            limitations=("insufficient or missing telemetry",),
        )
    compliance = len(good) / total
    budget = compliance - definition.objective
    burn = (1 - compliance) / max(1e-9, 1 - definition.objective)
    return SLOResult(
        slo_id=definition.id,
        status="met" if compliance >= definition.objective else "breached",
        good_events=len(good),
        total_events=total,
        objective=definition.objective,
        compliance=compliance,
        error_budget_remaining=budget,
        burn_rate=burn,
    )
