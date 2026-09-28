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

    @context_app.command("capsule")
    def context_capsule(
        target: str = typer.Option(..., "--target", help="Operation, e.g. 'POST /orders'."),
        root: Path = typer.Option(Path("."), "--root"),
        case_dir: Path | None = typer.Option(None, "--case", help="Default <root>/.apiforge/case."),
        budget_bytes: int = typer.Option(16000, "--budget-bytes", min=256),
        level: str = typer.Option("L3", "--level", help="Max expansion level L0-L4."),
        impact: str = typer.Option("transitive", "--impact", help="direct|transitive|all."),
        action: str = typer.Option("inspect", "--action"),
        objective: str = typer.Option("", "--objective"),
        run_id: str | None = typer.Option(None, "--run-id"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Minimal sufficient evidence for one operation as ctx:// refs under a byte budget."""
        from apiforge.application.context import build_context_capsule
        from apiforge.cli import _echo_json, _run

        _echo_json(
            _run(
                lambda: build_context_capsule(
                    root,
                    target=target,
                    case_dir=case_dir,
                    budget_bytes=budget_bytes,
                    level=level,
                    impact=impact,
                    action=action,
                    objective=objective,
                    run_id=run_id,
                )
            ),
            detail_level,
        )

    @context_app.command("expand")
    def context_expand(
        uri: str = typer.Argument(..., help="ctx://sha256/<hex> emitted by `context capsule`."),
        root: Path = typer.Option(Path("."), "--root"),
        run_id: str | None = typer.Option(None, "--run-id"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Return one ctx object after verifying its sha256."""
        from apiforge.application.context import expand_context_ref
        from apiforge.cli import _echo_json, _run

        _echo_json(_run(lambda: expand_context_ref(root, uri=uri, run_id=run_id)), detail_level)


__all__ = ["register"]
