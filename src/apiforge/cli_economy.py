"""Economy attribution commands: stats by run/source and rule-based explain."""

from __future__ import annotations

from pathlib import Path

import typer


def register(economy_app: typer.Typer) -> None:
    @economy_app.command("stats")
    def economy_stats(
        root: Path = typer.Option(Path("."), "--root"),
        run_id: str | None = typer.Option(None, "--run-id"),
        transcript: Path | None = typer.Option(
            None, "--transcript", help="Host transcript JSONL; unlocks observed tokens."
        ),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Bytes attributed per run and source; tokens stay unresolved without a transcript."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.run_ledger import stats

        _echo_json(_run(lambda: _with_tokens(stats(root, run_id=run_id), transcript)), detail_level)

    @economy_app.command("explain")
    def economy_explain(
        run_id: str = typer.Argument(..., help="run_id printed by `context capsule`."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Why each ref of a run was spent, from recorded provenance rules only."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.run_ledger import explain

        _echo_json(_run(lambda: explain(root, run_id)), detail_level)

    @economy_app.command("roi")
    def economy_roi(
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Per extra capability: calls, facts and unresolved added, outcome changed vs primary."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.roi import role_roi

        _echo_json(_run(lambda: role_roi(root)), detail_level)


def _with_tokens(payload: dict[str, object], transcript: Path | None) -> dict[str, object]:
    if transcript is None:
        return payload
    from apiforge.economy.tokens import read_transcript

    payload["tokens"] = read_transcript(transcript)
    payload["tokens_unresolved"] = False
    return payload


__all__ = ["register"]
