import pytest

textual = pytest.importorskip("textual")

from apiforge.tui.app import ForgeApp


def test_textual_app_has_execution_first_bindings() -> None:
    assert ForgeApp.TITLE.startswith("API Forge")
    assert ForgeApp.BINDINGS[0][0] == "d"
    assert {binding[0] for binding in ForgeApp.BINDINGS} >= {"d", "s", "v", "e", "n", "c", "g", "b"}


def test_textual_app_keeps_routing_in_the_canonical_view() -> None:
    assert "routing" not in ForgeApp.BINDINGS
