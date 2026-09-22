"""Provider-specific read transports with credentials owned by the host."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from apiforge.contracts.observability import ReadSafetyPolicy
from apiforge.observability.read_safety import evaluate_response


class ProviderRequester(Protocol):
    """Host-owned requester; it resolves the reference and sets auth headers."""

    def get(
        self,
        endpoint: str,
        params: Mapping[str, str],
        credential_reference: str,
    ) -> Mapping[str, object]: ...


def _records(provider: str, response: Mapping[str, object]) -> dict[str, object]:
    if isinstance(response.get("records"), (list, tuple)):
        return {"records": response["records"]}
    keys = {
        "datadog": "data",
        "dynatrace": "result",
        "cloudwatch": "Datapoints",
        "otel": "spans",
    }
    value = response.get(keys[provider])
    return {"records": value} if isinstance(value, (list, tuple)) else {"records": ()}


class ProviderReadTransport:
    """Concrete provider boundary; no HTTP client or credential store in core."""

    def __init__(
        self,
        provider: str,
        credential_reference: str,
        requester: ProviderRequester,
        policy: ReadSafetyPolicy | None = None,
    ) -> None:
        if provider not in {"otel", "datadog", "dynatrace", "cloudwatch"}:
            raise ValueError(f"AF-OBS-ADAPTER-PROVIDER: unsupported provider {provider!r}")
        self.provider = provider
        self.credential_reference = credential_reference
        self.requester = requester
        self.policy = policy or ReadSafetyPolicy()

    def get(self, endpoint: str, params: Mapping[str, str]) -> Mapping[str, object]:
        response = self.requester.get(endpoint, params, self.credential_reference)
        normalized = _records(self.provider, response)
        record_count, response_bytes, violations = evaluate_response(self.policy, normalized)
        if violations:
            return {
                "records": (),
                "safety_record_count": record_count,
                "safety_response_bytes": response_bytes,
                "safety_violations": violations,
            }
        return normalized


def provider_transport(
    provider: str,
    credential_reference: str,
    requester: ProviderRequester,
    policy: ReadSafetyPolicy | None = None,
) -> ProviderReadTransport:
    return ProviderReadTransport(provider, credential_reference, requester, policy)
