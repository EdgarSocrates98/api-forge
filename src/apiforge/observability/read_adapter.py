"""Transport-injected read adapters for authenticated providers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from apiforge.contracts.observability import CredentialStatus, ReadPlan, ReadReceipt


class ReadTransport(Protocol):
    """External boundary: the host owns HTTP, retries and credential headers."""

    def get(self, endpoint: str, params: Mapping[str, str]) -> Mapping[str, object]: ...


class ReadOnlyAdapter:
    def __init__(self, provider: str) -> None:
        self.provider = provider

    def execute(
        self,
        plan: ReadPlan,
        credential: CredentialStatus,
        transport: ReadTransport,
    ) -> ReadReceipt:
        if plan.provider != self.provider or credential.provider != self.provider:
            raise ValueError("AF-OBS-ADAPTER-PROVIDER: plan, credential and adapter must match")
        if credential.status != "available":
            return ReadReceipt(
                provider=plan.provider,
                status="blocked",
                credential_reference=credential.reference,
                record_count=0,
                evidence=(credential.reason, "network_called:false", "mutation_performed:false"),
            )
        response = transport.get(
            plan.endpoint,
            {
                "service": plan.query.service,
                "environment": plan.query.environment,
                "start": plan.query.start,
                "end": plan.query.end,
                "signals": ",".join(plan.query.signals),
            },
        )
        violations = response.get("safety_violations", ())
        if isinstance(violations, (list, tuple)) and violations:
            return ReadReceipt(
                provider=plan.provider,
                status="blocked",
                credential_reference=credential.reference,
                record_count=0,
                network_called=True,
                mutation_performed=False,
                violations=tuple(str(item) for item in violations),
                evidence=("safety-policy-rejected", "network_called:true", "mutation_performed:false"),
            )
        records = response.get("records", ())
        count = len(records) if isinstance(records, (list, tuple)) else 0
        return ReadReceipt(
            provider=plan.provider,
            status="executed",
            credential_reference=credential.reference,
            record_count=count,
            network_called=True,
            mutation_performed=False,
            evidence=("transport-injected", "GET", "read_only:true", "mutation_performed:false"),
        )


def adapter_for(provider: str) -> ReadOnlyAdapter:
    if provider not in {"otel", "datadog", "dynatrace", "cloudwatch"}:
        raise ValueError(f"AF-OBS-ADAPTER-PROVIDER: unsupported provider {provider!r}")
    return ReadOnlyAdapter(provider)
