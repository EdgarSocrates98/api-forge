"""Explicit host-owned authentication and endpoint binding for exports."""

from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from typing import Protocol
from urllib.parse import urlsplit

from apiforge.contracts.observability import (
    CircuitBreakerMetrics,
    CircuitMetricsExportReceipt,
    CredentialStatus,
    HostExportBinding,
)
from apiforge.observability.exporters import build_export_payload


class AuthenticatedExportSender(Protocol):
    """Host callback that resolves credentials and owns the authenticated request."""

    def __call__(
        self,
        endpoint: str,
        payload: Mapping[str, object],
        credential_reference: str,
    ) -> None: ...


def execute_host_export(
    metrics: CircuitBreakerMetrics,
    binding: HostExportBinding,
    credential: CredentialStatus,
    allowed_hosts: AbstractSet[str],
    sender: AuthenticatedExportSender | None = None,
) -> CircuitMetricsExportReceipt:
    def blocked(reason: str) -> CircuitMetricsExportReceipt:
        return CircuitMetricsExportReceipt(
            provider=binding.provider,
            backend=binding.backend,
            status="blocked",
            metric_count=4,
            credential_reference=binding.credential_reference,
            approval_id=binding.approval_id,
            violations=(reason,),
            evidence=(f"export-blocked:{reason}", "network_called:false"),
        )

    if binding.provider != metrics.provider:
        return blocked("provider-mismatch")
    if binding.backend != binding.provider:
        return blocked("backend-provider-mismatch")
    if (
        credential.provider != binding.provider
        or credential.reference != binding.credential_reference
    ):
        return blocked("credential-mismatch")
    if credential.status != "available":
        return blocked("credential-unavailable")
    if not binding.enabled:
        return blocked("binding-disabled")
    if not binding.approval_id:
        return blocked("approval-required")
    parsed = urlsplit(binding.endpoint)
    host = parsed.hostname.lower() if parsed.hostname else ""
    normalized_hosts = {item.lower().strip() for item in allowed_hosts}
    if (
        parsed.scheme != "https"
        or not host
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        return blocked("endpoint-must-be-https-and-credential-free")
    if host not in normalized_hosts:
        return blocked("endpoint-host-not-allowlisted")
    if sender is None:
        return blocked("sender-not-configured")
    payload = build_export_payload(binding.backend, metrics)
    try:
        sender(binding.endpoint, payload, binding.credential_reference)
    except (OSError, RuntimeError, TimeoutError) as exc:
        return CircuitMetricsExportReceipt(
            provider=binding.provider,
            backend=binding.backend,
            status="failed",
            metric_count=4,
            credential_reference=binding.credential_reference,
            approval_id=binding.approval_id,
            network_called=True,
            evidence=(f"export-error:{type(exc).__name__}", "network_called:true"),
        )
    return CircuitMetricsExportReceipt(
        provider=binding.provider,
        backend=binding.backend,
        status="sent",
        metric_count=4,
        credential_reference=binding.credential_reference,
        approval_id=binding.approval_id,
        network_called=True,
        evidence=("host-authenticated-callback", "approval-verified", "network_called:true"),
    )
