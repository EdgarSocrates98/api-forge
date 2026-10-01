from typer.testing import CliRunner

from apiforge.cli import app

runner = CliRunner()


def test_version_is_stable() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.stdout == "apiforge 0.1.0\n"


def test_help_lists_mvp_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("discover", "model", "diff", "judge"):
        assert command in result.stdout
