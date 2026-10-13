from typer.testing import CliRunner

from apiforge.cli import app


def test_capabilities_cli() -> None:
    result = CliRunner().invoke(app, ["observability", "capabilities"])
    assert result.exit_code == 0
    assert "datadog" in result.stdout
