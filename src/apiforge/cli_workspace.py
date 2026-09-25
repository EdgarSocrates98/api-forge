"""Virtual workspace commands for independent repositories."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, cast

import typer

workspace_app = typer.Typer(
    name="workspace",
    help="Register independent repositories in a local virtual workspace.",
    no_args_is_help=True,
)


def _emit(value: object, detail_level: str) -> None:
    from apiforge.cli import _echo_json, _run

    if is_dataclass(value):
        value = asdict(cast(Any, value))
    _echo_json(_run(lambda: value), detail_level)


@workspace_app.command("discover")
def workspace_discover(
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.workspace import discover

    _emit(discover(root), detail_level)


@workspace_app.command("init")
def workspace_init(
    root: Path = typer.Option(Path("."), "--root"),
    name: str | None = typer.Option(None, "--name"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.workspace import initialize

    _emit(initialize(root, name=name), detail_level)


@workspace_app.command("add")
def workspace_add(
    repository: Path = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.workspace import add

    _emit(add(root, repository), detail_level)


@workspace_app.command("status")
def workspace_status(
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.workspace import status

    _emit(status(root), detail_level)


def register(app: typer.Typer) -> None:
    app.add_typer(workspace_app, name="workspace")


__all__ = ["register", "workspace_app"]
