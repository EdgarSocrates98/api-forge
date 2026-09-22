"""Deterministic protobuf and gRPC evolution checks."""

from __future__ import annotations

from typing import Literal

from apiforge.contracts.grpc import GrpcCompatibilityReport, GrpcDiagnostic, GrpcIR, GrpcSeverity


def compare(baseline: GrpcIR, candidate: GrpcIR) -> GrpcCompatibilityReport:
    findings: list[GrpcDiagnostic] = []
    old_messages = {item.full_name: item for item in baseline.messages}
    new_messages = {item.full_name: item for item in candidate.messages}
    for name, old in old_messages.items():
        current_message = new_messages.get(name)
        if current_message is None:
            findings.append(
                GrpcDiagnostic(
                    code="GRPC-MESSAGE-REMOVED",
                    severity=GrpcSeverity.BREAKING,
                    message=f"message removed: {name}",
                    path=name,
                )
            )
            continue
        by_number = {field.number: field for field in current_message.fields}
        for field in old.fields:
            replacement = by_number.get(field.number)
            if replacement is None:
                findings.append(
                    GrpcDiagnostic(
                        code="GRPC-FIELD-REMOVED",
                        severity=GrpcSeverity.BREAKING,
                        message=f"field removed without reservation: {name}.{field.name}",
                        path=name,
                    )
                )
            elif replacement.type_name != field.type_name or replacement.label != field.label:
                findings.append(
                    GrpcDiagnostic(
                        code="GRPC-FIELD-TYPE-CHANGED",
                        severity=GrpcSeverity.BREAKING,
                        message=f"field type changed: {name}.{field.name}",
                        path=name,
                    )
                )
            elif replacement.name != field.name:
                findings.append(
                    GrpcDiagnostic(
                        code="GRPC-FIELD-NUMBER-REUSED",
                        severity=GrpcSeverity.BREAKING,
                        message=f"field number reused: {name}.{field.number}",
                        path=name,
                    )
                )
        old_by_name = {field.name: field for field in old.fields}
        for field in current_message.fields:
            previous = old_by_name.get(field.name)
            if previous and previous.number != field.number:
                findings.append(
                    GrpcDiagnostic(
                        code="GRPC-FIELD-NUMBER-CHANGED",
                        severity=GrpcSeverity.BREAKING,
                        message=f"field number changed: {name}.{field.name}",
                        path=name,
                    )
                )
    old_services = {item.full_name: item for item in baseline.services}
    new_services = {item.full_name: item for item in candidate.services}
    for name, old_service in old_services.items():
        current_service = new_services.get(name)
        if current_service is None:
            findings.append(GrpcDiagnostic(code="GRPC-SERVICE-REMOVED", severity=GrpcSeverity.BREAKING, message=f"service removed: {name}", path=name))
            continue
        current_rpcs = {rpc.name: rpc for rpc in current_service.rpcs}
        for rpc in old_service.rpcs:
            replacement_rpc = current_rpcs.get(rpc.name)
            if replacement_rpc is None:
                findings.append(GrpcDiagnostic(code="GRPC-RPC-REMOVED", severity=GrpcSeverity.BREAKING, message=f"rpc removed: {rpc.full_name}", path=rpc.full_name))
            elif replacement_rpc.stream_mode != rpc.stream_mode or replacement_rpc.request_type != rpc.request_type or replacement_rpc.response_type != rpc.response_type:
                findings.append(GrpcDiagnostic(code="GRPC-RPC-SIGNATURE-CHANGED", severity=GrpcSeverity.BREAKING, message=f"rpc signature changed: {rpc.full_name}", path=rpc.full_name))
    for enum_name, old_values in baseline.enum_values.items():
        new_values = set(candidate.enum_values.get(enum_name, ()))
        for value in old_values:
            if value not in new_values:
                findings.append(GrpcDiagnostic(code="GRPC-ENUM-VALUE-REMOVED", severity=GrpcSeverity.BREAKING, message=f"enum value removed: {enum_name}.{value}", path=enum_name))
    verdict: Literal["compatible", "review", "breaking", "inconclusive"] = (
        "breaking"
        if any(item.severity == GrpcSeverity.BREAKING for item in findings)
        else "compatible"
    )
    return GrpcCompatibilityReport(
        baseline_digest=baseline.source_sha256,
        candidate_digest=candidate.source_sha256,
        verdict=verdict,
        diagnostics=tuple(findings),
    )
