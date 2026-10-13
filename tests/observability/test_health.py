from apiforge.contracts.observability import SLOResult, TelemetryRecord
from apiforge.observability.health import assess_health


def _record(status_code: int, duration_ms: float = 10) -> TelemetryRecord:
    return TelemetryRecord(
        id=f"r-{status_code}",
        kind="span",
        service="orders",
        operation="GET /orders",
        status_code=status_code,
        duration_ms=duration_ms,
        source="fixture.json",
    )


def test_health_correlates_slo_and_performance_failure() -> None:
    result = assess_health(
        "orders",
        (_record(200), _record(500, 900)),
        (
            SLOResult(
                slo_id="availability",
                status="breached",
                good_events=1,
                total_events=2,
                objective=0.99,
            ),
        ),
        ("FAIL",),
    )

    assert result.status == "incident"
    assert result.severity == "critical"
    assert result.recommended_actions


def test_health_does_not_treat_missing_telemetry_as_healthy() -> None:
    result = assess_health("orders", ())

    assert result.status == "inconclusive"
    assert result.gaps == ("no telemetry records for service",)
