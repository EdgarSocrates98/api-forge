"""Canonical scoped context command registration."""

from __future__ import annotations

from pathlib import Path

import typer


def register(context_app: typer.Typer) -> None:
    @context_app.command("resolve")
    def context_resolve(
        root: Path = typer.Option(Path("."), "--root"),
        scope: str = typer.Option("repo", "--scope"),
        target: str | None = typer.Option(None, "--target"),
        impact: str | None = typer.Option(None, "--impact"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.application.context import resolve_context
        from apiforge.cli import _echo_json, _run

        _echo_json(
            _run(lambda: resolve_context(root, scope=scope, target=target, impact=impact)),
            detail_level,
        )


__all__ = ["register"]
