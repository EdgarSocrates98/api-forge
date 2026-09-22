from pathlib import Path

from apiforge.contracts.grpc import GrpcGatewayRequest
from apiforge.grpc.gateway import plan_gateway
from apiforge.grpc.source import load_source


def test_gateway_projections_are_local(tmp_path: Path) -> None:
    result = plan_gateway(load_source(Path("tests/fixtures/grpc/orders.proto")), GrpcGatewayRequest(gateways=("envoy", "grpc_gateway", "grpc_web", "openapi"), output_dir=str(tmp_path)))
    assert all(item.status == "projected" for item in result)
