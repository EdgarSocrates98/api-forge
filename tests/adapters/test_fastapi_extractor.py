from pathlib import Path

from apiforge.adapters.fastapi.extractor import extract_fastapi


def test_missing_router_binding_is_unresolved_not_a_traceback() -> None:
    root = Path(__file__).resolve().parents[2]
    inventory = extract_fastapi(root)
    assert any(item.code == "AF-FASTAPI-UNRESOLVED-BINDING" for item in inventory.diagnostics)
    assert inventory.execution.status in {"completed", "partial"}
