"""CLI command group for the optional TUI surface."""

from __future__ import annotations

from pathlib import Path

import typer

from apiforge.tui import run_tui

tui_app = typer.Typer(
    name="tui",
    help="Execution-first terminal UX with a Rich/JSON fallback.",
    invoke_without_command=True,
)


@tui_app.callback()
def tui(
    task_id: str = typer.Argument(..., help="TaskSpec id to inspect or execute."),
    root: Path = typer.Option(Path("."), "--root", help="Project root."),
    fallback: bool = typer.Option(False, "--fallback", help="Force headless projection."),
) -> None:
    """Open the canonical execution and governance projection."""
    run_tui(root, task_id, force_fallback=fallback)


__all__ = ["tui_app"]
