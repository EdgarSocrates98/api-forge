from pathlib import Path

from apiforge.grpc.compatibility import compare
from apiforge.grpc.source import load_source


def test_type_change_is_breaking() -> None:
    result = compare(
        load_source(Path("tests/fixtures/grpc/orders.proto")),
        load_source(Path("tests/fixtures/grpc/orders-breaking.proto")),
    )
    assert result.verdict == "breaking"
    assert any(item.code == "GRPC-FIELD-TYPE-CHANGED" for item in result.diagnostics)
