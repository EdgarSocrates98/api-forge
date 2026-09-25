"""Portable distribution commands over canonical application services."""

from __future__ import annotations

from pathlib import Path

import typer

distribution_app = typer.Typer(
    name="distribution",
    help="Inspect the installed package, paths and hostless capabilities.",
    no_args_is_help=True,
)


def _emit(value: object, detail_level: str) -> None:
    from apiforge.cli import _echo_json, _run

    _echo_json(_run(lambda: value), detail_level)


@distribution_app.command("inspect")
def distribution_inspect(
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.portable import inspect

    _emit(inspect(root), detail_level)


@distribution_app.command("init")
def distribution_init(
    root: Path = typer.Option(Path("."), "--root"),
    workspace: bool = typer.Option(False, "--workspace"),
    name: str | None = typer.Option(None, "--name"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.portable import initialize

    _emit(initialize(root, workspace=workspace, name=name), detail_level)


@distribution_app.command("status")
def distribution_status(
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.portable import status

    _emit(status(root), detail_level)


@distribution_app.command("doctor")
def distribution_doctor(
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.portable import doctor

    _emit(doctor(root), detail_level)


def register(app: typer.Typer) -> None:
    app.add_typer(distribution_app, name="distribution")


__all__ = ["distribution_app", "register"]
