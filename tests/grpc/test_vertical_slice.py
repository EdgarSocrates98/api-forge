from pathlib import Path

from apiforge.contracts.grpc import GrpcCodegenRequest
from apiforge.grpc.codegen import plan_codegen
from apiforge.grpc.compatibility import compare
from apiforge.grpc.source import load_source
from apiforge.grpc.verify import verify


def test_vertical_slice_returns_review_for_breaking_contract(tmp_path: Path) -> None:
    baseline = load_source(Path("tests/fixtures/grpc/orders.proto"))
    candidate = load_source(Path("tests/fixtures/grpc/orders-breaking.proto"))
    result = verify(candidate, compare(baseline, candidate), plan_codegen(candidate, GrpcCodegenRequest(output_dir=str(tmp_path))))
    assert result.verdict == "REVIEW"
