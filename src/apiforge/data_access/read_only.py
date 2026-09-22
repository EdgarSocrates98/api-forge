"""Host-injected read-only data and broker adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from apiforge.contracts.data_runtime import DataReadReceipt, DataReadRequest
from apiforge.core.ids import stable_id
from apiforge.runtime.store import content_hash


class DataRequester(Protocol):
    def read(self, request: DataReadRequest) -> Mapping[str, object]: ...


_WRITE_WORDS = frozenset(
    {
        "put",
        "post",
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "publish",
        "send",
        "produce",
        "write",
        "execute_write",
        "mutate",
        "create",
        "truncate",
    }
)


def _is_mutation(operation: str) -> bool:
    normalized = operation.strip().lower().replace("-", "_")
    return normalized in _WRITE_WORDS or any(word in normalized.split("_") for word in _WRITE_WORDS)


class ReadOnlyDataAdapter:
    """Credential-free core boundary for databases, streams and brokers."""

    def execute(self, request: DataReadRequest, requester: DataRequester) -> DataReadReceipt:
        if _is_mutation(request.operation):
            return DataReadReceipt(
                provider=request.provider,
                resource_ref=request.resource_ref,
                operation=request.operation,
                status="blocked",
                mutation_performed=False,
                violations=("AF-DATA-READONLY-MUTATION",),
                evidence=("network_called:false", "mutation_performed:false"),
            )
        try:
            response = requester.read(request)
        except (ConnectionError, TimeoutError, OSError, RuntimeError) as exc:
            return DataReadReceipt(
                provider=request.provider,
                resource_ref=request.resource_ref,
                operation=request.operation,
                status="failed",
                network_called=True,
                mutation_performed=False,
                violations=(f"request_failed:{type(exc).__name__}",),
                evidence=("network_called:true", "mutation_performed:false"),
            )
        digest = content_hash(response)
        return DataReadReceipt(
            provider=request.provider,
            resource_ref=request.resource_ref,
            operation=request.operation,
            status="executed",
            network_called=True,
            mutation_performed=False,
            response_digest=digest,
            evidence=(
                f"response:{stable_id('data-response', {'digest': digest})}",
                "network_called:true",
                "mutation_performed:false",
                "credential_source:host",
            ),
            limitations=("response content is not persisted by the core adapter",),
        )
