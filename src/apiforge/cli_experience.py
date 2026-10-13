"""Modular command group for the canonical runtime experience.

The legacy top-level aliases remain in ``cli.py``.  This group gives new
surfaces one explicit home while delegating to the same application facade.
"""

from __future__ import annotations

from pathlib import Path

import typer

experience_app = typer.Typer(
    name="experience",
    help="Canonical execution, governance and evidence projections.",
    no_args_is_help=True,
)


def _emit(value: object, detail_level: str) -> None:
    """Emit the application result, including canonical routing artifacts."""
    # Import lazily so the legacy CLI remains the composition root.
    from apiforge.cli import _echo_json, _run

    _echo_json(_run(lambda: value), detail_level)


@experience_app.command("status")
def experience_status(
    task_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.runtime_experience import status

    _emit(status(root, task_id), detail_level)


@experience_app.command("doctor")
def experience_doctor(
    task_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.runtime_experience import doctor

    _emit(doctor(root, task_id), detail_level)


@experience_app.command("review")
def experience_review(
    task_id: str = typer.Argument(...),
    root: Path = typer.Option(Path("."), "--root"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    from apiforge.application.runtime_experience import review

    _emit(review(root, task_id), detail_level)


def register(app: typer.Typer) -> None:
    """Attach the modular group to the legacy application."""
    app.add_typer(experience_app, name="experience")


__all__ = ["experience_app", "register"]
