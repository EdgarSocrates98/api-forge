"""Read-first integration gateway for external engineering systems."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from apiforge.contracts.platform import CapabilityRecord, CapabilityRequest, CapabilityResult
from apiforge.core.models import JsonValue


class IntegrationAdapter(Protocol):
    """Minimal adapter surface shared by Git, CI/CD, cloud and data tools."""

    name: str

    def capabilities(self) -> tuple[CapabilityRecord, ...]: ...

    def execute(self, request: CapabilityRequest) -> CapabilityResult: ...


class IntegrationGateway:
    """Dispatch integration requests while keeping mutation behind a gate."""

    def __init__(self, adapters: tuple[IntegrationAdapter, ...] = ()) -> None:
        self._adapters = {adapter.name: adapter for adapter in adapters}

    def register(self, adapter: IntegrationAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def capabilities(self) -> tuple[CapabilityRecord, ...]:
        records = [
            record for adapter in self._adapters.values() for record in adapter.capabilities()
        ]
        return tuple(sorted(records, key=lambda item: item.capability_id))

    def execute(
        self,
        request: CapabilityRequest,
        *,
        adapter: str,
        allow_external_mutation: bool = False,
        approved: bool = False,
        rollback: str | None = None,
    ) -> CapabilityResult:
        selected = self._adapters.get(adapter)
        if selected is None:
            return CapabilityResult(
                capability_id=request.capability_id,
                state="unsupported",
                status="blocked",
                gaps=(f"adapter {adapter!r} is not registered",),
                error_code="AF-INTEGRATION-UNSUPPORTED",
            )
        if request.action == "apply" and (
            not allow_external_mutation or not approved or not rollback
        ):
            return CapabilityResult(
                capability_id=request.capability_id,
                state="unsupported",
                status="blocked",
                gaps=("external mutation requires policy, approval and rollback",),
                error_code="AF-INTEGRATION-GATE",
            )
        return selected.execute(request)


class StaticIntegrationAdapter:
    """Deterministic adapter useful for local fixtures and contract tests."""

    def __init__(
        self,
        name: str,
        records: tuple[CapabilityRecord, ...],
        payloads: Mapping[str, Mapping[str, JsonValue]] | None = None,
    ) -> None:
        self.name = name
        self._records = records
        self._payloads = dict(payloads or {})

    def capabilities(self) -> tuple[CapabilityRecord, ...]:
        return self._records

    def execute(self, request: CapabilityRequest) -> CapabilityResult:
        record = next(
            (item for item in self._records if item.capability_id == request.capability_id),
            None,
        )
        if record is None:
            return CapabilityResult(
                capability_id=request.capability_id,
                state="unsupported",
                status="blocked",
                error_code="AF-INTEGRATION-CAPABILITY",
                gaps=("capability is not declared by adapter",),
            )
        raw = self._payloads.get(request.capability_id, {})
        return CapabilityResult(
            capability_id=request.capability_id,
            state=record.state,
            status="ok" if record.state == "supported" else "review",
            payload=raw,
            evidence=record.evidence,
            limitations=record.limitations,
        )
