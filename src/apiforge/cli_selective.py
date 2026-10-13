"""Selective-agentics commands: lazy expertise, referee packets and the agent uniqueness gate."""

from __future__ import annotations

from pathlib import Path

import typer


def register(knowledge_app: typer.Typer, debate_app: typer.Typer, agents_app: typer.Typer) -> None:
    @knowledge_app.command("select")
    def knowledge_select_cmd(
        intent: str = typer.Option(..., "--intent", help="What the task is about."),
        capability: str | None = typer.Option(None, "--capability"),
        framework: list[str] = typer.Option([], "--framework", help="Observed framework."),
        root: Path | None = typer.Option(None, "--root", help="Directory of knowledge packs."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Only the packs a declared trigger names; no trigger means no packs."""
        from apiforge.application.selective import knowledge_select
        from apiforge.cli import _echo_json, _run

        _echo_json(
            _run(
                lambda: knowledge_select(
                    intent, capability=capability, frameworks=framework, root=root
                )
            ),
            detail_level,
        )

    @debate_app.command("packet")
    def debate_packet_cmd(
        case: Path = typer.Option(..., "--case", help="Case directory."),
        debate: str = typer.Option(..., "--debate", help="Debate id."),
        capsule: str | None = typer.Option(None, "--capsule", help="Shared ctx:// capsule id."),
        root: Path = typer.Option(Path("."), "--root", help="Where the capsule was built."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Referee input: shared capsule id + one position delta per side + disagreements."""
        from apiforge.application.selective import debate_packet
        from apiforge.cli import _echo_json, _run

        _echo_json(
            _run(lambda: debate_packet(case, debate, capsule_id=capsule, root=root)),
            detail_level,
        )

    @agents_app.command("audit")
    def agents_audit_cmd(
        root: Path = typer.Option(Path("."), "--root", help="Repository root."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Anti-agentic-theater gate: unique capability/expertise/validator/tool/decision role."""
        from apiforge.application.selective import agents_audit
        from apiforge.cli import _echo_json, _run

        _echo_json(_run(lambda: agents_audit(root)), detail_level)


__all__ = ["register"]
