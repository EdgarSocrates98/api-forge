"""Tool/host economy commands: log slicing, MCP surface cost and host projections."""

from __future__ import annotations

from pathlib import Path

import typer


def register(app: typer.Typer, agentops_app: typer.Typer) -> None:
    slice_app = typer.Typer(
        name="slice",
        help="Failures and signatures instead of whole logs; the full log stays behind ctx://.",
        no_args_is_help=True,
    )
    mcp_app = typer.Typer(
        name="mcp", help="MCP surface projections and their measured cost.", no_args_is_help=True
    )
    app.add_typer(slice_app)
    app.add_typer(mcp_app)

    @slice_app.command("tests")
    def slice_tests_cmd(
        input_path: Path = typer.Option(..., "--input", help="pytest output or JUnit XML."),
        fmt: str = typer.Option("auto", "--format", help="auto|pytest|junit."),
        root: Path = typer.Option(Path("."), "--root", help="Where the full log is stored."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Counts plus every failing test with file:line and assertion."""
        from apiforge.agentops.slicing import slice_tests
        from apiforge.cli import _echo_json, _run

        _echo_json(_run(lambda: slice_tests(root, input_path, fmt)), detail_level)

    @slice_app.command("log")
    def slice_log_cmd(
        input_path: Path = typer.Option(..., "--input", help="CI or build log."),
        root: Path = typer.Option(Path("."), "--root", help="Where the full log is stored."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Deduplicated failure signatures with frames, preceding context and environment."""
        from apiforge.agentops.slicing import slice_log
        from apiforge.cli import _echo_json, _run

        _echo_json(_run(lambda: slice_log(root, input_path)), detail_level)

    @mcp_app.command("surface")
    def mcp_surface_cmd(
        surface: str = typer.Option("full", "--surface", help="full|compact."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Name, description and schema bytes of every tool on a surface."""
        from apiforge.cli import _echo_json, _run
        from apiforge.mcp.surface import measure_surface

        _echo_json(_run(lambda: measure_surface(surface)), detail_level)

    @agentops_app.command("projection")
    def agentops_projection_cmd(
        host: str = typer.Option(..., "--host", help="claude|gpt-codex|devin|copilot."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Declared economical projection for a host, with measured surface bytes."""
        from apiforge.agentops.projection import project_host
        from apiforge.cli import _echo_json, _run

        _echo_json(_run(lambda: project_host(host)), detail_level)


__all__ = ["register"]
