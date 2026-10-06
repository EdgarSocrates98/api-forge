from pathlib import Path

from apiforge.grpc.source import load_source


def test_grpc_eval_fixture_has_streaming_service() -> None:
    ir = load_source(Path("tests/fixtures/grpc/orders.proto"))
    assert any(
        rpc.stream_mode.value == "bidirectional_streaming"
        for service in ir.services
        for rpc in service.rpcs
    )
