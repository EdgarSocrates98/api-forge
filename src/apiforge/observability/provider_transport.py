"""Provider-specific read transports with credentials owned by the host."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol


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

    def __init__(self, provider: str, credential_reference: str, requester: ProviderRequester) -> None:
        if provider not in {"otel", "datadog", "dynatrace", "cloudwatch"}:
            raise ValueError(f"AF-OBS-ADAPTER-PROVIDER: unsupported provider {provider!r}")
        self.provider = provider
        self.credential_reference = credential_reference
        self.requester = requester

    def get(self, endpoint: str, params: Mapping[str, str]) -> Mapping[str, object]:
        response = self.requester.get(endpoint, params, self.credential_reference)
        return _records(self.provider, response)


def provider_transport(provider: str, credential_reference: str, requester: ProviderRequester) -> ProviderReadTransport:
    return ProviderReadTransport(provider, credential_reference, requester)
