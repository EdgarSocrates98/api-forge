import pytest

from apiforge.contracts.observability import CredentialStatus
from apiforge.observability.read import build_read_plan
from apiforge.observability.read_adapter import adapter_for


class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, str]]] = []

    def get(self, endpoint: str, params: dict[str, str]) -> dict[str, object]:
        self.calls.append((endpoint, params))
        return {"records": [{"id": "span-1"}, {"id": "span-2"}]}


def test_authenticated_read_is_transport_injected_and_non_mutating() -> None:
    plan = build_read_plan("datadog", "orders", "start", "end")
    credential = CredentialStatus(
        provider="datadog",
        reference="broker:datadog/orders",
        status="available",
        reason="resolved by external broker",
    )
    transport = FakeTransport()

    receipt = adapter_for("datadog").execute(plan, credential, transport)

    assert receipt.status == "executed"
    assert receipt.record_count == 2
    assert receipt.network_called is True
    assert receipt.mutation_performed is False
    assert transport.calls[0][1]["service"] == "orders"


def test_unavailable_credential_blocks_before_transport() -> None:
    plan = build_read_plan("dynatrace", "orders", "start", "end")
    credential = CredentialStatus(
        provider="dynatrace",
        reference="DYNATRACE_TOKEN",
        status="blocked",
        reason="broker unavailable",
    )
    transport = FakeTransport()

    receipt = adapter_for("dynatrace").execute(plan, credential, transport)

    assert receipt.status == "blocked"
    assert receipt.network_called is False
    assert transport.calls == []


def test_adapter_rejects_provider_mismatch() -> None:
    plan = build_read_plan("cloudwatch", "orders", "start", "end")
    credential = CredentialStatus(
        provider="cloudwatch",
        reference="aws:profile",
        status="available",
        reason="broker",
    )

    with pytest.raises(ValueError, match="AF-OBS-ADAPTER-PROVIDER"):
        adapter_for("datadog").execute(plan, credential, FakeTransport())
