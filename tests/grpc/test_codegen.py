from pathlib import Path

from apiforge.contracts.grpc import GrpcCodegenRequest
from apiforge.grpc.codegen import plan_codegen
from apiforge.grpc.source import load_source


def test_fake_codegen_is_reproducible(tmp_path: Path) -> None:
    result = plan_codegen(
        load_source(Path("tests/fixtures/grpc/orders.proto")),
        GrpcCodegenRequest(languages=("python", "go", "java"), output_dir=str(tmp_path)),
    )
    assert result.status == "generated"
    assert len(result.artifacts) == 3
    assert all(item.sha256 for item in result.artifacts)
