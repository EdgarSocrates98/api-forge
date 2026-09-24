import pytest

textual = pytest.importorskip("textual")

from apiforge.tui.app import ForgeApp


def test_textual_app_has_execution_first_bindings() -> None:
    assert ForgeApp.TITLE.startswith("API Forge")
    assert ForgeApp.BINDINGS[0][0] == "d"
    assert {binding[0] for binding in ForgeApp.BINDINGS} >= {"d", "s", "v", "e", "n", "c", "g", "b"}
