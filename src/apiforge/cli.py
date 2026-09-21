from collections.abc import Callable

import typer

from apiforge import __version__

app = typer.Typer(
    help="Analyze API evolution deterministically and offline.",
    invoke_without_command=True,
)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the API Forge version and exit.",
        is_eager=True,
    ),
) -> None:
    """Analyze API evolution deterministically and offline."""
    if version:
        typer.echo(f"apiforge {__version__}")
        raise typer.Exit()


def unavailable_command(name: str) -> Callable[[], None]:
    """Create a bounded placeholder for an MVP command."""

    def command() -> None:
        typer.echo(f"AF-COMMAND-NOT-AVAILABLE: {name}")
        raise typer.Exit(code=2)

    return command


for command_name in ("discover", "model", "diff", "judge"):
    app.command(name=command_name)(unavailable_command(command_name))
