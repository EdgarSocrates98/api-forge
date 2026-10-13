from apiforge.adapters.fastapi.models import FastApiInventory
from apiforge.adapters.inventory import CodeInventory


def test_fastapi_inventory_is_a_code_inventory() -> None:
    inv = FastApiInventory(root="x")
    assert isinstance(inv, CodeInventory)
    assert inv.framework == "fastapi"
    assert inv.facts == () and inv.input_hashes == {}


def test_code_inventory_requires_framework() -> None:
    inv = CodeInventory(framework="spring", root="x")
    assert inv.framework == "spring"
