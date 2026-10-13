from apiforge.contracts.observability import CredentialStatus, HostExportBinding
from apiforge.observability.readiness import assess_export_readiness


def _binding(**over: object) -> HostExportBinding:
    values: dict[str, object] = {
        "provider": "datadog",
        "backend": "datadog",
        "endpoint": "https://api.datadoghq.com/api/v2/series",
        "credential_reference": "secret/datadog",
        "approval_id": "approval-1",
        "enabled": True,
    }
    values.update(over)
    return HostExportBinding.model_validate(values)


def _credential(**over: object) -> CredentialStatus:
    values: dict[str, object] = {
        "provider": "datadog",
        "reference": "secret/datadog",
        "status": "available",
        "reason": "host broker resolved metadata",
    }
    values.update(over)
    return CredentialStatus.model_validate(values)


def test_ready_preflight_is_network_free() -> None:
    result = assess_export_readiness(
        _binding(), _credential(), {"api.datadoghq.com"}, sender_configured=True
    )
    assert result.status == "ready"
    assert result.network_called is False
    assert result.blockers == ()


def test_missing_approval_or_sender_is_review() -> None:
    result = assess_export_readiness(
        _binding(approval_id=None), _credential(), {"api.datadoghq.com"}
    )
    assert result.status == "review"
    assert "approval-required" in result.blockers


def test_credential_or_endpoint_mismatch_is_blocked() -> None:
    result = assess_export_readiness(
        _binding(endpoint="http://evil.example/export"),
        _credential(status="unavailable"),
        {"api.datadoghq.com"},
        sender_configured=True,
    )
    assert result.status == "blocked"
    assert "credential-unavailable" in result.blockers
    assert "endpoint-must-be-https-and-credential-free" in result.blockers
