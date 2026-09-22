"""Host-owned HTTPS requester boundary for provider read adapters."""

from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from typing import Protocol
from urllib.parse import urlsplit


class HttpGet(Protocol):
    """Host implementation that owns sockets, headers, retries and timeouts."""

    def __call__(
        self,
        endpoint: str,
        params: Mapping[str, str],
        credential_reference: str,
    ) -> Mapping[str, object]: ...


class HostHttpRequester:
    """Validate an explicitly allowed HTTPS endpoint before delegating to the host."""

    def __init__(self, allowed_hosts: AbstractSet[str], http_get: HttpGet) -> None:
        if not allowed_hosts or any(not host.strip() for host in allowed_hosts):
            raise ValueError("AF-OBS-HTTP-ALLOWLIST: at least one host is required")
        self.allowed_hosts = frozenset(host.lower().strip() for host in allowed_hosts)
        self.http_get = http_get

    def get(
        self,
        endpoint: str,
        params: Mapping[str, str],
        credential_reference: str,
    ) -> Mapping[str, object]:
        parsed = urlsplit(endpoint)
        host = parsed.hostname.lower() if parsed.hostname else ""
        if parsed.scheme != "https" or not host or parsed.username or parsed.password:
            raise ValueError("AF-OBS-HTTP-ENDPOINT: only credential-free HTTPS endpoints are allowed")
        if parsed.fragment or "{" in endpoint or "}" in endpoint:
            raise ValueError("AF-OBS-HTTP-ENDPOINT: endpoint must be resolved and fragment-free")
        if host not in self.allowed_hosts:
            raise ValueError(f"AF-OBS-HTTP-ALLOWLIST: host {host!r} is not allowed")
        return self.http_get(endpoint, params, credential_reference)


def host_http_requester(allowed_hosts: AbstractSet[str], http_get: HttpGet) -> HostHttpRequester:
    return HostHttpRequester(allowed_hosts, http_get)
