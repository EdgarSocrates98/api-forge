"""Provider-specific read transports with credentials owned by the host."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from time import sleep
from typing import Protocol

from apiforge.contracts.observability import ReadRetryPolicy, ReadSafetyPolicy
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
        retry_policy: ReadRetryPolicy | None = None,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        if provider not in {"otel", "datadog", "dynatrace", "cloudwatch"}:
            raise ValueError(f"AF-OBS-ADAPTER-PROVIDER: unsupported provider {provider!r}")
        self.provider = provider
        self.credential_reference = credential_reference
        self.requester = requester
        self.policy = policy or ReadSafetyPolicy()
        self.retry_policy = retry_policy or ReadRetryPolicy()
        self.sleeper = sleeper

    def get(self, endpoint: str, params: Mapping[str, str]) -> Mapping[str, object]:
        response: Mapping[str, object] | None = None
        attempts = 0
        for attempts in range(1, self.retry_policy.max_attempts + 1):
            try:
                response = self.requester.get(endpoint, params, self.credential_reference)
                break
            except (ConnectionError, TimeoutError, OSError):
                if attempts >= self.retry_policy.max_attempts:
                    raise
                delay = min(
                    self.retry_policy.base_backoff_seconds * (2 ** (attempts - 1)),
                    self.retry_policy.max_backoff_seconds,
                )
                self.sleeper(delay)
        if response is None:
            raise RuntimeError("AF-OBS-REQUEST: requester returned no response")
        normalized = _records(self.provider, response)
        record_count, response_bytes, violations = evaluate_response(self.policy, normalized)
        if violations:
            return {
                "records": (),
                "request_attempts": attempts,
                "safety_record_count": record_count,
                "safety_response_bytes": response_bytes,
                "safety_violations": violations,
            }
        normalized["request_attempts"] = attempts
        return normalized


def provider_transport(
    provider: str,
    credential_reference: str,
    requester: ProviderRequester,
    policy: ReadSafetyPolicy | None = None,
    retry_policy: ReadRetryPolicy | None = None,
    sleeper: Callable[[float], None] = sleep,
) -> ProviderReadTransport:
    return ProviderReadTransport(
        provider, credential_reference, requester, policy, retry_policy, sleeper
    )
