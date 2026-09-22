from apiforge.contracts.observability import SLODefinition, TelemetryRecord


def test_observability_contracts_are_frozen_and_versioned() -> None:
    record = TelemetryRecord(id="1", kind="span", service="orders")
    assert record.version == 1
    assert SLODefinition(id="slo", service="orders", objective=0.99, window_seconds=60).objective == 0.99
