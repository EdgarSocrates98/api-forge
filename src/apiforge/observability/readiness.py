"""Offline readiness diagnostics for observability exports."""

from __future__ import annotations

from collections.abc import Set as AbstractSet
from typing import Literal, cast
from urllib.parse import urlsplit

from apiforge.contracts.observability import (
    CredentialStatus,
    HostExportBinding,
    ObservabilityExportReadiness,
)


def assess_export_readiness(
    binding: HostExportBinding,
    credential: CredentialStatus,
    allowed_hosts: AbstractSet[str],
    *,
    sender_configured: bool = False,
) -> ObservabilityExportReadiness:
    """Check export prerequisites without resolving secrets or making a request."""

    checks: list[str] = []
    blockers: list[str] = []

    if binding.provider != binding.backend:
        blockers.append("backend-provider-mismatch")
    else:
        checks.append("backend-provider-match")
    if credential.provider != binding.provider or credential.reference != binding.credential_reference:
        blockers.append("credential-mismatch")
    elif credential.status != "available":
        blockers.append("credential-unavailable")
    else:
        checks.append("credential-metadata-match")
    if not binding.enabled:
        blockers.append("binding-disabled")
    else:
        checks.append("binding-enabled")
    if not binding.approval_id:
        blockers.append("approval-required")
    else:
        checks.append("approval-present")

    parsed = urlsplit(binding.endpoint)
    host = parsed.hostname.lower() if parsed.hostname else ""
    normalized_hosts = {item.lower().strip() for item in allowed_hosts}
    if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.fragment:
        blockers.append("endpoint-must-be-https-and-credential-free")
    elif host not in normalized_hosts:
        blockers.append("endpoint-host-not-allowlisted")
    else:
        checks.append("endpoint-allowlisted")
    if not sender_configured:
        blockers.append("sender-not-configured")
    else:
        checks.append("sender-configured")

    status = "ready" if not blockers else "blocked"
    if blockers and all(item in {"sender-not-configured", "approval-required"} for item in blockers):
        status = "review"
    return ObservabilityExportReadiness(
        provider=binding.provider,
        status=cast(Literal["ready", "review", "blocked"], status),
        checks=tuple(checks),
        blockers=tuple(blockers),
        network_called=False,
    )
