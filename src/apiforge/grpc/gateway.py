"""Gateway projection facade."""

from __future__ import annotations

from apiforge.contracts.grpc import GrpcGatewayProjection, GrpcGatewayRequest, GrpcIR
from apiforge.grpc.gateway_adapters import project


def plan_gateway(ir: GrpcIR, request: GrpcGatewayRequest) -> tuple[GrpcGatewayProjection, ...]:
    return tuple(project(ir, gateway, request.output_dir) for gateway in request.gateways)
