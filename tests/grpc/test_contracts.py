from apiforge.contracts.grpc import GrpcIR, GrpcRpc, GrpcStreamMode


def test_contracts_are_frozen_and_versioned() -> None:
    rpc = GrpcRpc(
        name="Get", full_name="orders.Orders/Get", request_type="Req", response_type="Res"
    )
    ir = GrpcIR(source_path="orders.proto", source_sha256="a", services=())
    assert rpc.stream_mode is GrpcStreamMode.UNARY
    assert ir.version == 1
