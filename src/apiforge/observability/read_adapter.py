"""Transport-injected read adapters for authenticated providers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from apiforge.contracts.observability import CredentialStatus, ReadPlan, ReadReceipt
from apiforge.observability.query import build_provider_params


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
            build_provider_params(plan),
        )
        circuit_violations = response.get("circuit_violations", ())
        if isinstance(circuit_violations, (list, tuple)) and circuit_violations:
            network_called = response.get("network_called", False)
            state = response.get("circuit_state", "unknown")
            return ReadReceipt(
                provider=plan.provider,
                status="blocked",
                credential_reference=credential.reference,
                record_count=0,
                network_called=network_called is True,
                mutation_performed=False,
                violations=tuple(str(item) for item in circuit_violations),
                evidence=(f"circuit_state:{state}", f"network_called:{str(network_called).lower()}"),
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
        attempts = response.get("request_attempts", 1)
        attempt_evidence = f"request_attempts:{attempts}" if isinstance(attempts, int) else "request_attempts:unknown"
        pages = response.get("page_count", 1)
        page_evidence = f"page_count:{pages}" if isinstance(pages, int) else "page_count:unknown"
        circuit_state = response.get("circuit_state", "unknown")
        circuit_evidence = f"circuit_state:{circuit_state}"
        return ReadReceipt(
            provider=plan.provider,
            status="executed",
            credential_reference=credential.reference,
            record_count=count,
            network_called=True,
            mutation_performed=False,
            evidence=("transport-injected", "GET", attempt_evidence, page_evidence, circuit_evidence, "read_only:true", "mutation_performed:false"),
        )


def adapter_for(provider: str) -> ReadOnlyAdapter:
    if provider not in {"otel", "datadog", "dynatrace", "cloudwatch"}:
        raise ValueError(f"AF-OBS-ADAPTER-PROVIDER: unsupported provider {provider!r}")
    return ReadOnlyAdapter(provider)
