from apiforge.contracts.observability import CircuitBreakerMetrics
from apiforge.observability.exporters import build_export_payload, export_metrics


def metrics() -> CircuitBreakerMetrics:
    return CircuitBreakerMetrics(
        provider="datadog",
        failures=2,
        openings=1,
        blocked_calls=3,
        recoveries=1,
        state="closed",
        alerts=("provider_circuit_open:datadog",),
    )


def test_export_payloads_have_backend_specific_shapes_without_secrets() -> None:
    otel = build_export_payload("otel", metrics())
    datadog = build_export_payload("datadog", metrics())
    dynatrace = build_export_payload("dynatrace", metrics())

    assert "resourceMetrics" in otel
    assert "series" in datadog
    assert "gauge" in dynatrace
    assert "secret" not in str(otel).lower()


def test_exporter_is_disabled_without_explicit_sender() -> None:
    receipt = export_metrics("otel", metrics())

    assert receipt.status == "disabled"
    assert receipt.network_called is False


def test_exporter_sends_only_through_injected_callback() -> None:
    sent: list[dict[str, object]] = []

    receipt = export_metrics("datadog", metrics(), sent.append)

    assert receipt.status == "sent"
    assert receipt.network_called is True
    assert len(sent) == 1


def test_exporter_reports_callback_failure_without_leaking_payload() -> None:
    def fail(_payload: object) -> None:
        raise RuntimeError("downstream unavailable")

    receipt = export_metrics("dynatrace", metrics(), fail)

    assert receipt.status == "failed"
    assert receipt.evidence == ("export-error:RuntimeError", "network_called:true")
