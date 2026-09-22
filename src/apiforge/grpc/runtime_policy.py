"""Declarative safety rules for gRPC runtime behavior."""

from __future__ import annotations

from apiforge.contracts.grpc import GrpcIR, GrpcRuntimePolicy


def default_policy() -> GrpcRuntimePolicy:
    return GrpcRuntimePolicy()


def validate_policy(ir: GrpcIR, policy: GrpcRuntimePolicy) -> tuple[str, ...]:
    gaps: list[str] = []
    for service in ir.services:
        for rpc in service.rpcs:
            if (
                policy.max_attempts > 1
                and not rpc.idempotent
                and not policy.allow_non_idempotent_retry
            ):
                gaps.append(f"retry-refused:{rpc.full_name}")
    return tuple(gaps)


def evaluate_deadline(elapsed_ms: float, policy: GrpcRuntimePolicy) -> dict[str, object]:
    exceeded = elapsed_ms > policy.deadline_ms
    return {"status": "DEADLINE_EXCEEDED" if exceeded else "OK", "retry_allowed": False if exceeded else policy.max_attempts > 1}


def runtime_capabilities(policy: GrpcRuntimePolicy) -> dict[str, object]:
    return {"health_check": policy.health_check, "reflection": policy.reflection, "deadline_ms": policy.deadline_ms, "max_message_bytes": policy.max_message_bytes}
