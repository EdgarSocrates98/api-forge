from pathlib import Path

from apiforge.grpc.source import load_source


def test_json_descriptor_preserves_services_and_http_projection() -> None:
    ir = load_source(Path("tests/fixtures/grpc/orders.descriptor.json"))
    rpc = ir.services[0].rpcs[0]
    assert ir.descriptor_sha256
    assert rpc.http_method == "GET"
    assert rpc.http_path == "/v1/orders/{order_id}"
