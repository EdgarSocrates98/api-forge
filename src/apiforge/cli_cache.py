"""Cache commands: layered freshness-aware cache stats and dependency-aware invalidation."""

from __future__ import annotations

from pathlib import Path

import typer


def register(app: typer.Typer) -> None:
    cache_app = typer.Typer(
        name="cache",
        help="Advisory layered cache — reuse only fresh evidence, invalidate by dependency.",
        no_args_is_help=True,
    )
    app.add_typer(cache_app)

    @cache_app.command("stats")
    def cache_stats_cmd(
        root: Path = typer.Option(Path("."), "--root"),
        cache_home: Path | None = typer.Option(None, "--cache-home", help="Shared cache tier."),
        layer: str | None = typer.Option(None, "--layer", help="Check one layer's policy."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Entries, bytes, expired and corrupt counts per layer and tier, plus policies."""
        from apiforge.application.cache import cache_lookup_layer, cache_stats
        from apiforge.cli import _echo_json, _run

        if layer is not None:
            _echo_json(_run(lambda: cache_lookup_layer(layer)), detail_level)
            return
        _echo_json(_run(lambda: cache_stats(root, cache_home=cache_home)), detail_level)

    @cache_app.command("invalidate")
    def cache_invalidate_cmd(
        changed: list[str] = typer.Option([], "--changed", help="Changed file (repeatable)."),
        base: str | None = typer.Option(None, "--base"),
        head: str | None = typer.Option(None, "--head"),
        root: Path = typer.Option(Path("."), "--root"),
        case_dir: Path | None = typer.Option(None, "--case"),
        cache_home: Path | None = typer.Option(None, "--cache-home"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Drop only the capsule selections whose dependencies intersect the change set."""
        from apiforge.application.cache import cache_invalidate
        from apiforge.cli import _echo_json, _run

        _echo_json(
            _run(
                lambda: cache_invalidate(
                    root,
                    changed=changed,
                    base=base,
                    head=head,
                    case_dir=case_dir,
                    cache_home=cache_home,
                )
            ),
            detail_level,
        )


__all__ = ["register"]
