"""Deterministic codegen planning facade."""

from __future__ import annotations

from apiforge.contracts.grpc import GrpcCodegenRequest, GrpcCodegenResult, GrpcIR
from apiforge.grpc.codegen_adapters import generate


def plan_codegen(ir: GrpcIR, request: GrpcCodegenRequest) -> GrpcCodegenResult:
    return generate(ir, request)
