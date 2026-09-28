"""Economy wave 8 commands: freshness watch, live gating, escalation, phase budgets, checkpoints."""

from __future__ import annotations

from pathlib import Path

import typer


def register(
    *,
    knowledge_app: typer.Typer,
    evidence_app: typer.Typer,
    verify_app: typer.Typer,
    economy_app: typer.Typer,
    runtime_app: typer.Typer,
) -> None:
    @knowledge_app.command("watch")
    def knowledge_watch_cmd(
        manifest: Path = typer.Option(..., "--manifest", help="Local upstream fingerprint JSON."),
        now: str = typer.Option(..., "--now", help="Explicit ISO8601 clock."),
        root: Path | None = typer.Option(None, "--root", help="Directory of knowledge packs."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Packs whose upstream fingerprint, version or expiry says refresh_needed (never fetches)."""
        from apiforge.cli import _echo_json, _run
        from apiforge.knowledge.watch import watch_packs

        _echo_json(_run(lambda: watch_packs(manifest, now=now, root=root)), detail_level)

    @evidence_app.command("gate")
    def evidence_gate_cmd(
        question: str = typer.Option(..., "--question"),
        mode: str | None = typer.Option(None, "--mode", help="Requested evidence mode."),
        offline: bool = typer.Option(False, "--offline", help="No live access in this run."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Cheapest evidence mode for a question; live_read_only only for runtime questions."""
        from apiforge.cli import _echo_json, _run
        from apiforge.evidence.live_gate import gate

        _echo_json(_run(lambda: gate(question, requested=mode, offline=offline)), detail_level)

    @verify_app.command("escalate")
    def verify_escalate_cmd(
        static: str = typer.Option("missing", "--static", help="missing|likely|clear|inconclusive"),
        test: str | None = typer.Option(None, "--test", help="missing|passed|failed|inconclusive"),
        test_slice: Path | None = typer.Option(None, "--test-slice", help="TestSlice/v1 JSON."),
        runtime: str = typer.Option(
            "missing", "--runtime", help="missing|confirmed|clear|inconclusive"
        ),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Next verification step: static → test → stop; runtime read-only only if inconclusive."""
        from apiforge.cli import _echo_json, _run
        from apiforge.verification.progressive import escalate

        _echo_json(
            _run(
                lambda: escalate(static=static, test=test, runtime=runtime, test_slice=test_slice)
            ),
            detail_level,
        )

    @economy_app.command("phase-budget")
    def economy_phase_budget_cmd(
        profile: str = typer.Option("balanced", "--profile"),
        usage: Path | None = typer.Option(None, "--usage", help="Per-phase usage JSON."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Profile envelope split across SDD phases; protected phases are never cut."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.phase_budget import load_usage, plan_phase_budgets

        _echo_json(
            _run(
                lambda: plan_phase_budgets(
                    profile, usage=load_usage(usage) if usage is not None else None
                )
            ),
            detail_level,
        )

    @runtime_app.command("checkpoint")
    def runtime_checkpoint_cmd(
        task_id: str = typer.Argument(...),
        run_id: str = typer.Argument(...),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Budget a run already spent, as a resume will continue it."""
        from apiforge.cli import _echo_json, _run
        from apiforge.runtime.economy_checkpoint import show_checkpoint

        _echo_json(_run(lambda: show_checkpoint(root, task_id, run_id)), detail_level)


__all__ = ["register"]
