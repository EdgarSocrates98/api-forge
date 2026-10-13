import pytest

from apiforge.observability.read import build_read_plan, fixture_receipt


def test_read_plan_is_vendor_specific_but_network_disabled() -> None:
    plan = build_read_plan("datadog", "orders", "2026-09-22T00:00:00Z", "2026-09-22T01:00:00Z")

    assert plan.endpoint.startswith("https://api.datadoghq.com")
    assert plan.read_only is True
    assert plan.network_allowed is False
    assert plan.execution_mode == "fixture_only"


def test_fixture_receipt_never_claims_provider_access() -> None:
    plan = build_read_plan("cloudwatch", "orders", "start", "end")
    receipt = fixture_receipt(plan, 3)

    assert receipt["status"] == "fixture_only"
    assert receipt["network_called"] is False
    assert receipt["credential_used"] is False


def test_unknown_provider_fails_closed() -> None:
    with pytest.raises(ValueError, match="AF-OBS-READ-PROVIDER"):
        build_read_plan("newrelic", "orders", "start", "end")
