from collections.abc import Mapping

from apiforge.contracts.observability import (
    CircuitBreakerMetrics,
    CredentialStatus,
    HostExportBinding,
)
from apiforge.observability.host_export import execute_host_export


def metrics() -> CircuitBreakerMetrics:
    return CircuitBreakerMetrics(
        provider="datadog",
        failures=1,
        openings=1,
        blocked_calls=1,
        recoveries=0,
        state="open",
    )


def binding(**overrides: object) -> HostExportBinding:
    values: dict[str, object] = {
        "provider": "datadog",
        "backend": "datadog",
        "endpoint": "https://api.datadoghq.com/api/v2/series",
        "credential_reference": "broker:dd",
        "approval_id": "approval-123",
        "enabled": True,
    }
    values.update(overrides)
    return HostExportBinding(**values)


def credential() -> CredentialStatus:
    return CredentialStatus(provider="datadog", reference="broker:dd", status="available", reason="broker")


def test_host_export_requires_explicit_approval_and_calls_authenticated_sender() -> None:
    calls: list[tuple[str, str, str]] = []

    def sender(endpoint: str, payload: Mapping[str, object], reference: str) -> None:
        calls.append((endpoint, str(payload["series"]), reference))

    receipt = execute_host_export(metrics(), binding(), credential(), {"api.datadoghq.com"}, sender)

    assert receipt.status == "sent"
    assert receipt.approval_id == "approval-123"
    assert calls[0][0].startswith("https://")
    assert calls[0][2] == "broker:dd"


def test_host_export_blocks_without_approval_or_sender() -> None:
    no_approval = execute_host_export(
        metrics(), binding(approval_id=None), credential(), {"api.datadoghq.com"}, lambda *_args: None
    )
    no_sender = execute_host_export(metrics(), binding(), credential(), {"api.datadoghq.com"})

    assert no_approval.status == "blocked"
    assert no_approval.network_called is False
    assert no_sender.violations == ("sender-not-configured",)


def test_host_export_blocks_unavailable_credential_and_untrusted_endpoint() -> None:
    unavailable = CredentialStatus(provider="datadog", reference="broker:dd", status="unavailable", reason="missing")
    blocked_credential = execute_host_export(metrics(), binding(), unavailable, {"api.datadoghq.com"}, lambda *_args: None)
    blocked_host = execute_host_export(metrics(), binding(), credential(), {"evil.example"}, lambda *_args: None)

    assert blocked_credential.violations == ("credential-unavailable",)
    assert blocked_host.violations == ("endpoint-host-not-allowlisted",)
