from typer.testing import CliRunner

from apiforge.cli import app

runner = CliRunner()


def test_version_is_stable() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout == "apiforge 0.1.3\n"


def test_help_lists_mvp_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("discover", "model", "diff", "judge"):
        assert command in result.stdout


def test_help_is_cp1252_safe() -> None:
    # Windows console default: a help char outside cp1252 (e.g. U+2192 `→`
    # in the `ai` docstring) made `apiforge --help` crash with
    # UnicodeEncodeError when rich wrote the panel to the console.
    # Rich auto-degrades its own borders; the *text* is the risk surface.
    click = __import__("pytest").importorskip("click")
    import typer.main

    root = typer.main.get_command(app)
    queue = [root]
    texts: list[str] = []
    while queue:
        cmd = queue.pop()
        texts.extend(t for t in (cmd.help, cmd.short_help) if t)
        texts.extend(p.help for p in getattr(cmd, "params", []) if p.help)
        if isinstance(cmd, click.Group):
            queue.extend(cmd.commands.values())
    for text in texts:
        assert text.encode("cp1252", errors="strict") is not None
