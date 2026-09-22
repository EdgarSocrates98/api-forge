"""Provider-specific read transports with credentials owned by the host."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from time import sleep
from typing import Protocol, cast

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


def _next_page(provider: str, response: Mapping[str, object]) -> str | None:
    if provider == "dynatrace" and isinstance(response.get("nextPageKey"), str):
        return cast(str, response["nextPageKey"])
    if provider == "cloudwatch" and isinstance(response.get("NextToken"), str):
        return cast(str, response["NextToken"])
    if provider == "otel" and isinstance(response.get("next_page_token"), str):
        return cast(str, response["next_page_token"])
    meta = response.get("meta")
    if provider == "datadog" and isinstance(meta, Mapping):
        page = meta.get("page")
        if isinstance(page, Mapping) and isinstance(page.get("after"), str):
            return cast(str, page["after"])
    return None


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
        attempts = 0
        page_count = 0
        next_token: str | None = None
        all_records: list[object] = []
        violations: tuple[str, ...] = ()
        record_count = 0
        response_bytes = 0
        while page_count < self.policy.max_pages:
            page_params = dict(params)
            if next_token:
                page_params["page_token"] = next_token
            response: Mapping[str, object] | None = None
            for attempt in range(1, self.retry_policy.max_attempts + 1):
                attempts += 1
                try:
                    response = self.requester.get(endpoint, page_params, self.credential_reference)
                    break
                except (ConnectionError, TimeoutError, OSError):
                    if attempt >= self.retry_policy.max_attempts:
                        raise
                    delay = min(
                        self.retry_policy.base_backoff_seconds * (2 ** (attempt - 1)),
                        self.retry_policy.max_backoff_seconds,
                    )
                    self.sleeper(delay)
            if response is None:
                raise RuntimeError("AF-OBS-REQUEST: requester returned no response")
            page_count += 1
            page_records = _records(self.provider, response).get("records", ())
            if isinstance(page_records, (list, tuple)):
                all_records.extend(page_records)
            normalized: dict[str, object] = {"records": all_records}
            record_count, response_bytes, violations = evaluate_response(self.policy, normalized)
            next_token = _next_page(self.provider, response)
            if violations or not next_token:
                break
        if next_token and page_count >= self.policy.max_pages and not violations:
            violations = (f"max_pages_exceeded:{self.policy.max_pages}",)
        normalized = {"records": all_records}
        if violations:
            return {
                "records": (),
                "request_attempts": attempts,
                "page_count": page_count,
                "safety_record_count": record_count,
                "safety_response_bytes": response_bytes,
                "safety_violations": violations,
            }
        normalized["request_attempts"] = attempts
        normalized["page_count"] = page_count
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
