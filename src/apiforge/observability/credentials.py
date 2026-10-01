"""Credential boundary: metadata in, secret values never exposed by the core."""

from __future__ import annotations

from apiforge.contracts.observability import (
    CredentialReference,
    CredentialStatus,
    ReadPlan,
    ReadReceipt,
)


def check_reference(
    provider: str, reference: str, source: str = "external_broker"
) -> CredentialStatus:
    if provider not in {"otel", "datadog", "dynatrace", "cloudwatch"}:
        raise ValueError(f"AF-OBS-CREDENTIAL-PROVIDER: unsupported provider {provider!r}")
    if not reference.strip():
        raise ValueError("AF-OBS-CREDENTIAL-REFERENCE: reference must not be empty")
    if source not in {"env", "ssm", "secrets_manager", "keychain", "external_broker"}:
        raise ValueError(f"AF-OBS-CREDENTIAL-SOURCE: unsupported source {source!r}")
    # The local core deliberately does not inspect environment variables or stores.
    return CredentialStatus(
        provider=provider,  # type: ignore[arg-type]
        reference=reference,
        status="blocked",
        reason="credential broker is not configured; no secret was read",
        evidence=("metadata-only", "secret_values_never_returned:true"),
    )


def reference(
    provider: str, reference_name: str, source: str = "external_broker"
) -> CredentialReference:
    if provider not in {"otel", "datadog", "dynatrace", "cloudwatch"}:
        raise ValueError(f"AF-OBS-CREDENTIAL-PROVIDER: unsupported provider {provider!r}")
    if not reference_name.strip():
        raise ValueError("AF-OBS-CREDENTIAL-REFERENCE: reference must not be empty")
    return CredentialReference(
        provider=provider,  # type: ignore[arg-type]
        reference=reference_name,
        source=source,  # type: ignore[arg-type]
    )


def execute_read_gate(
    plan: ReadPlan, credential: CredentialStatus, record_count: int = 0
) -> ReadReceipt:
    """Gate future provider execution; current core only permits fixture evidence."""
    if record_count < 0:
        raise ValueError("AF-OBS-READ-COUNT: record_count must be non-negative")
    if credential.status != "available":
        return ReadReceipt(
            provider=plan.provider,
            status="blocked",
            credential_reference=credential.reference,
            record_count=0,
            evidence=(credential.reason, "network_called:false", "mutation_performed:false"),
        )
    if record_count:
        return ReadReceipt(
            provider=plan.provider,
            status="fixture_only",
            credential_reference=credential.reference,
            record_count=record_count,
            evidence=("fixture-input", "network_called:false", "mutation_performed:false"),
        )
    return ReadReceipt(
        provider=plan.provider,
        status="blocked",
        credential_reference=credential.reference,
        record_count=0,
        evidence=(
            "live adapter not configured",
            "network_called:false",
            "mutation_performed:false",
        ),
    )
