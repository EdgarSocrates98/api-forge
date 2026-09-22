from apiforge.observability.normalize import normalize_records
from apiforge.observability.signals import summarize


def test_red_signals_are_deterministic() -> None:
    records = normalize_records((
        {"kind": "span", "service": "orders", "operation": "/orders", "duration_ms": 10, "status_code": 200},
        {"kind": "span", "service": "orders", "operation": "/orders", "duration_ms": 30, "status_code": 500},
    ))
    summary = summarize(records, duration_seconds=2)
    assert summary[0].request_count == 2
    assert summary[0].error_rate == 0.5
    assert summary[0].throughput_tps == 1
