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
        no_cache: bool = typer.Option(False, "--no-cache", help="Skip L3/L4 cache lookups."),
        cache_home: Path | None = typer.Option(None, "--cache-home", help="Shared cache tier."),
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
                    cache=False if no_cache else None,
                    cache_home=cache_home,
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

    @context_app.command("delta")
    def context_delta_cmd(
        base: str | None = typer.Option(None, "--base", help="Base ref (read-only git diff)."),
        head: str | None = typer.Option(None, "--head", help="Head ref; default worktree."),
        changed: list[str] = typer.Option([], "--changed", help="Changed file (repeatable)."),
        root: Path = typer.Option(Path("."), "--root"),
        case_dir: Path | None = typer.Option(None, "--case"),
        invalidate: bool = typer.Option(False, "--invalidate", help="Drop affected selections."),
        cache_home: Path | None = typer.Option(None, "--cache-home"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """What changed, which operations it impacts and which capsules to build — delta first."""
        from apiforge.application.cache import context_delta
        from apiforge.cli import _echo_json, _run

        _echo_json(
            _run(
                lambda: context_delta(
                    root,
                    changed=changed,
                    base=base,
                    head=head,
                    case_dir=case_dir,
                    invalidate=invalidate,
                    cache_home=cache_home,
                )
            ),
            detail_level,
        )

    @context_app.command("quality")
    def context_quality(
        capsule: Path = typer.Option(
            ..., "--capsule", help="Recorded capsule JSON (`context capsule ... > capsule.json`)."
        ),
        run_id: str = typer.Option(..., "--run-id"),
        root: Path = typer.Option(Path("."), "--root"),
        required: list[str] = typer.Option(
            [], "--required", help="ctx:// uri declared required for recall (repeatable)."
        ),
        gate: str = typer.Option("strict", "--gate", help="strict|evidence|permissive."),
        cache_hits: int | None = typer.Option(None, "--cache-hits"),
        cache_lookups: int | None = typer.Option(None, "--cache-lookups"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Measured context quality + minimum-sufficient decision for one capsule."""
        from apiforge.application.context import context_quality_report
        from apiforge.cli import _echo_json, _run

        _echo_json(
            _run(
                lambda: context_quality_report(
                    root,
                    capsule_path=capsule,
                    run_id=run_id,
                    required_uris=tuple(required),
                    gate=gate,
                    cache_hits=cache_hits,
                    cache_lookups=cache_lookups,
                )
            ),
            detail_level,
        )

    @context_app.command("gc")
    def context_gc_cmd(
        root: Path = typer.Option(Path("."), "--root"),
        apply: bool = typer.Option(False, "--apply", help="Delete; default only reports."),
        cache_home: Path | None = typer.Option(None, "--cache-home"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Expired/corrupt cache entries, orphan cache objects and unreferenced ctx objects."""
        from apiforge.application.cache import context_gc
        from apiforge.cli import _echo_json, _run

        _echo_json(_run(lambda: context_gc(root, apply=apply, cache_home=cache_home)), detail_level)


__all__ = ["register"]
