"""TUI/menu contract tests — vendored ui.* surface."""

import pytest


def test_menu_well_formed():
    """Every _MENU item is a (label, argv|None) pair — no bare strings."""
    from apiforge.ui import home

    for item in home._MENU:
        assert isinstance(item, tuple) and len(item) == 2, item
        label, argv = item
        assert isinstance(label, str) and label
        assert argv is None or argv == "__wizard__" or isinstance(argv, list)


def test_menu_argv_parse_on_real_cli():
    """Every menu argv names a real command path — `--help` on it exits 0.

    Shape-only checks let `install mcp-verify` (a verb that never existed)
    sit in the menu; parsing each entry against the live Typer app catches
    invented commands.
    """
    from typer.testing import CliRunner

    from apiforge.cli import app
    from apiforge.ui import home

    runner = CliRunner()
    for label, argv in home._MENU:
        if argv is None or argv == "__wizard__":
            continue
        result = runner.invoke(app, [*argv, "--help"])
        assert result.exit_code == 0, (label, argv, result.output[-400:])


def test_tui_entries_real():
    from apiforge.ui import tui

    entries = tui.entries()
    assert len(entries) >= 3
    assert any("wizard" in e.label for e in entries)


def test_tui_renders_non_tty_ctx():
    from apiforge.ui import tui
    from apiforge.ui.app import ForgeApp
    from apiforge.ui.kit import UIContext
    from apiforge.ui.screen import Buffer

    ctx = UIContext(interactive=False, color=False, unicode=False, width=80, height=24, ansi=False)
    app = ForgeApp(ctx, forge_id="x", title="cc", entries=tui.entries())
    buf = Buffer(ctx, 80, 24)
    app.render(buf)
    assert "menu" in chr(10).join(buf.render())


def test_home_requires_tty():
    from apiforge.ui import home
    from apiforge.ui.kit import NonInteractive, UIContext

    ctx = UIContext(interactive=False, color=False, unicode=False, width=80)
    with pytest.raises(NonInteractive):
        home.run_home(ctx=ctx)
