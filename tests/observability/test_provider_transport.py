from collections.abc import Mapping

from apiforge.contracts.observability import (
    CircuitBreakerPolicy,
    CredentialStatus,
    ReadRetryPolicy,
    ReadSafetyPolicy,
)
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
        assert any(value == "orders" or "service:orders" in value for value in params.values())
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


def test_transient_request_is_retried_with_bounded_backoff() -> None:
    class FlakyRequester(FakeProviderRequester):
        failures = 1

        def get(self, endpoint: str, params: Mapping[str, str], credential_reference: str) -> Mapping[str, object]:
            if self.failures:
                self.failures -= 1
                raise TimeoutError("temporary")
            return super().get(endpoint, params, credential_reference)

    delays: list[float] = []
    requester = FlakyRequester({"data": [{"id": "trace-1"}]})
    plan = build_read_plan("datadog", "orders", "start", "end")
    credential = CredentialStatus(provider="datadog", reference="broker:dd", status="available", reason="resolved")
    transport = provider_transport(
        "datadog",
        credential.reference,
        requester,
        retry_policy=ReadRetryPolicy(max_attempts=2, base_backoff_seconds=0.1),
        sleeper=delays.append,
    )

    receipt = adapter_for("datadog").execute(plan, credential, transport)

    assert receipt.status == "executed"
    assert receipt.record_count == 1
    assert "request_attempts:2" in receipt.evidence
    assert delays == [0.1]


def test_pagination_is_bounded_and_accumulated() -> None:
    class PagedRequester:
        def get(self, endpoint: str, params: Mapping[str, str], credential_reference: str) -> Mapping[str, object]:
            if params.get("page_token") == "after-1":
                return {"data": [{"id": "trace-2"}]}
            return {"data": [{"id": "trace-1"}], "meta": {"page": {"after": "after-1"}}}

    plan = build_read_plan("datadog", "orders", "start", "end")
    credential = CredentialStatus(provider="datadog", reference="broker:dd", status="available", reason="resolved")
    transport = provider_transport(
        "datadog", credential.reference, PagedRequester(), ReadSafetyPolicy(max_pages=2)
    )

    receipt = adapter_for("datadog").execute(plan, credential, transport)

    assert receipt.status == "executed"
    assert receipt.record_count == 2
    assert "page_count:2" in receipt.evidence


def test_pagination_limit_blocks_unfinished_page_chain() -> None:
    class EndlessRequester:
        def get(self, endpoint: str, params: Mapping[str, str], credential_reference: str) -> Mapping[str, object]:
            token = params.get("page_token", "next")
            return {"data": [{"id": token}], "meta": {"page": {"after": token + "-next"}}}

    plan = build_read_plan("datadog", "orders", "start", "end")
    credential = CredentialStatus(provider="datadog", reference="broker:dd", status="available", reason="resolved")
    transport = provider_transport(
        "datadog", credential.reference, EndlessRequester(), ReadSafetyPolicy(max_pages=1)
    )

    receipt = adapter_for("datadog").execute(plan, credential, transport)

    assert receipt.status == "blocked"
    assert receipt.violations == ("max_pages_exceeded:1",)


def test_circuit_breaker_transitions_open_half_open_and_closed() -> None:
    class FlakyRequester:
        def __init__(self) -> None:
            self.calls = 0

        def get(self, endpoint: str, params: Mapping[str, str], credential_reference: str) -> Mapping[str, object]:
            self.calls += 1
            if self.calls < 3:
                raise TimeoutError("provider down")
            return {"data": [{"id": "trace-1"}]}

    now = [0.0]
    requester = FlakyRequester()
    plan = build_read_plan("datadog", "orders", "start", "end")
    credential = CredentialStatus(provider="datadog", reference="broker:dd", status="available", reason="resolved")
    transport = provider_transport(
        "datadog",
        credential.reference,
        requester,
        retry_policy=ReadRetryPolicy(max_attempts=1),
        circuit_policy=CircuitBreakerPolicy(failure_threshold=2, recovery_timeout_seconds=10),
        clock=lambda: now[0],
    )

    first = adapter_for("datadog").execute(plan, credential, transport)
    second = adapter_for("datadog").execute(plan, credential, transport)
    blocked = adapter_for("datadog").execute(plan, credential, transport)
    now[0] = 11.0
    probe = adapter_for("datadog").execute(plan, credential, transport)

    assert first.violations == ("provider_transient_failure",)
    assert second.violations == ("provider_transient_failure",)
    assert blocked.violations == ("circuit_open",)
    assert blocked.network_called is False
    assert "circuit_state:closed" in probe.evidence
    assert probe.status == "executed"
