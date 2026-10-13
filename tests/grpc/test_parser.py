from pathlib import Path

from apiforge.grpc.source import load_source


def test_parser_builds_messages_services_and_all_stream_modes() -> None:
    ir = load_source(Path("tests/fixtures/grpc/orders.proto"))
    assert ir.package == "orders.v1"
    assert {item.name for item in ir.messages} == {"OrderRequest", "Order"}
    assert ir.services[0].rpcs[1].stream_mode.value == "bidirectional_streaming"
