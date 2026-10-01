from apiforge.contracts.observability import SLODefinition
from apiforge.observability.normalize import normalize_records
from apiforge.observability.slo import evaluate_slo


def test_slo_reports_breach() -> None:
    records = normalize_records(({"kind": "span", "service": "orders", "status_code": 500},))
    result = evaluate_slo(
        SLODefinition(id="orders", service="orders", objective=0.99, window_seconds=60), records
    )
    assert result.status == "breached"
