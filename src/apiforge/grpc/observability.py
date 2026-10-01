"""Map gRPC facts to provider-neutral observability attributes."""

from __future__ import annotations

from apiforge.contracts.grpc import GrpcIR


def rpc_attributes(ir: GrpcIR) -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "rpc.system": "grpc",
            "rpc.service": service.full_name,
            "rpc.method": rpc.name,
            "rpc.stream_mode": rpc.stream_mode.value,
        }
        for service in ir.services
        for rpc in service.rpcs
    )


def normalize_otel_records(records: list[dict[str, object]]) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "service": str(item.get("service", "unknown")),
            "operation": item.get("rpc.method") or item.get("operation"),
            "status_code": item.get("status_code"),
            "correlation_id": item.get("trace_id"),
            "stream_mode": item.get("rpc.stream_mode", "unary"),
        }
        for item in records
    )
