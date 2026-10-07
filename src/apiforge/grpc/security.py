"""Credential-safe gRPC policy checks."""

from __future__ import annotations

import re

from apiforge.contracts.grpc import GrpcSecurityReport

_SECRET = re.compile(r"(?i)(authorization|token|password|secret|api[-_]?key)")


def inspect_metadata(metadata: dict[str, str]) -> GrpcSecurityReport:
    redacted = tuple(sorted(key for key in metadata if _SECRET.search(key)))
    return GrpcSecurityReport(safe=True, redacted_fields=redacted)


def authorize_mutation(approved: bool, brokered: bool) -> GrpcSecurityReport:
    if approved and brokered:
        return GrpcSecurityReport(safe=True)
    return GrpcSecurityReport(
        safe=False, findings=("external mutation requires approval and broker",)
    )
