from collections.abc import Mapping

from apiforge.contracts.observability import CredentialStatus, ReadSafetyPolicy
from apiforge.observability.provider_transport import provider_transport
from apiforge.observability.read import build_read_plan
from apiforge.observability.read_adapter import adapter_for


class FakeProviderRequester:
    def __init__(self, payload: Mapping[str, object]) -> None:
        self.payload = payload
        self.references: list[str] = []

    def get(self, endpoint: str, params: Mapping[str, str], credential_reference: str) -> Mapping[str, object]:
        self.references.append(credential_reference)
        assert endpoint.startswith("https://")
        assert params["service"] == "orders"
        return self.payload


def test_datadog_response_is_normalized_without_secret() -> None:
    requester = FakeProviderRequester({"data": [{"id": "trace-1"}]})
    plan = build_read_plan("datadog", "orders", "start", "end")
    credential = CredentialStatus(provider="datadog", reference="broker:dd", status="available", reason="resolved")

    receipt = adapter_for("datadog").execute(plan, credential, provider_transport("datadog", credential.reference, requester))

    assert receipt.record_count == 1
    assert requester.references == ["broker:dd"]


def test_cloudwatch_datapoints_are_normalized() -> None:
    requester = FakeProviderRequester({"Datapoints": [{"Average": 10}, {"Average": 20}]})
    plan = build_read_plan("cloudwatch", "orders", "start", "end")
    credential = CredentialStatus(provider="cloudwatch", reference="broker:aws", status="available", reason="resolved")

    receipt = adapter_for("cloudwatch").execute(plan, credential, provider_transport("cloudwatch", credential.reference, requester))

    assert receipt.record_count == 2
    assert receipt.mutation_performed is False


def test_response_over_budget_is_rejected_after_network_read() -> None:
    requester = FakeProviderRequester({"data": [{"id": "trace-1"}, {"id": "trace-2"}]})
    plan = build_read_plan("datadog", "orders", "start", "end")
    credential = CredentialStatus(provider="datadog", reference="broker:dd", status="available", reason="resolved")
    transport = provider_transport(
        "datadog", credential.reference, requester, ReadSafetyPolicy(max_records=1)
    )

    receipt = adapter_for("datadog").execute(plan, credential, transport)

    assert receipt.status == "blocked"
    assert receipt.network_called is True
    assert receipt.violations == ("max_records_exceeded:2>1",)
