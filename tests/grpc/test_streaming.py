from pathlib import Path

from apiforge.contracts.grpc import GrpcRuntimePolicy
from apiforge.grpc.source import load_source
from apiforge.grpc.streaming import analyze_streams


def test_streaming_analysis_is_bounded() -> None:
    result = analyze_streams(load_source(Path("tests/fixtures/grpc/orders.proto")), GrpcRuntimePolicy())
    assert result["bounded"] is True
