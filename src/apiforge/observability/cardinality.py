"""Cardinality budget checks."""

from apiforge.contracts.observability import ObservabilityFinding, TelemetryRecord
from apiforge.observability.redaction import cardinality


def findings(records: tuple[TelemetryRecord, ...], budget: int = 100) -> tuple[ObservabilityFinding, ...]:
    result = []
    for record in records:
        value = cardinality(record.attributes)
        if value > budget:
            result.append(ObservabilityFinding(id=f"cardinality:{record.id}", severity="high", title="Cardinality budget exceeded", detail=f"{value}>{budget}", evidence=(record.id,), status="confirmed"))
    return tuple(result)
