"""Economy wave 7 commands: verification plans, retrieval, evidence refs, doctor, tiers, prompts."""

from __future__ import annotations

from pathlib import Path

import typer


def register(
    app: typer.Typer,
    *,
    knowledge_app: typer.Typer,
    evidence_app: typer.Typer,
    economy_app: typer.Typer,
    agentops_app: typer.Typer,
    workspace_app: typer.Typer,
) -> None:
    verify_app = typer.Typer(
        name="verify", help="Targeted verification plans (never executes).", no_args_is_help=True
    )
    app.add_typer(verify_app)

    @verify_app.command("plan")
    def verify_plan_cmd(
        changed: list[str] = typer.Option([], "--changed", help="Changed file (repeatable)."),
        risk: str = typer.Option("low", "--risk", help="micro|low|medium|high (sdd classify)."),
        breaking: bool = typer.Option(False, "--breaking", help="Contract verdict is breaking."),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Ladder level for the risk plus the impacted tests and the commands to run them."""
        from apiforge.cli import _echo_json, _run
        from apiforge.verification.selection import plan_verification

        _echo_json(
            _run(lambda: plan_verification(root, changed, risk=risk, breaking=breaking)),
            detail_level,
        )

    @knowledge_app.command("search")
    def knowledge_search_cmd(
        query: str = typer.Option(..., "--query"),
        tier: int = typer.Option(1, "--tier", help="1 = top 3, 2 = top 5, 3 = up to 20."),
        root: Path | None = typer.Option(None, "--root", help="Directory of knowledge packs."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Deterministic expansion, ranked passages with signals, progressive tiers."""
        from apiforge.cli import _echo_json, _run
        from apiforge.knowledge.retrieval import search

        _echo_json(_run(lambda: search(query, tier=tier, root=root)), detail_level)

    @evidence_app.command("resolve")
    def evidence_resolve_cmd(
        ref: str = typer.Argument(..., help="evidence://{operation|fact|finding|rule}/<id>"),
        root: Path = typer.Option(Path("."), "--root"),
        case_dir: Path | None = typer.Option(None, "--case"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """One evidence node with one-hop neighbors as further evidence:// refs."""
        from apiforge.cli import _echo_json, _run
        from apiforge.evidence.resolve import resolve

        _echo_json(_run(lambda: resolve(root, ref, case_dir=case_dir)), detail_level)

    @economy_app.command("doctor")
    def economy_doctor_cmd(
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """What in this setup makes runs pay more than needed, with the unlock for each."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.doctor import diagnose

        _echo_json(_run(lambda: diagnose(root)), detail_level)

    @economy_app.command("providers")
    def economy_providers_cmd(detail_level: str = typer.Option("normal", "--detail-level")) -> None:
        """Declared provider capabilities and deterministic capabilities."""
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.providers import list_providers

        _echo_json(_run(list_providers), detail_level)

    @economy_app.command("tier")
    def economy_tier_cmd(
        capability: str = typer.Option(..., "--capability"),
        risk: str = typer.Option("low", "--risk"),
        family: str | None = typer.Option(None, "--family"),
        root: Path = typer.Option(Path("."), "--root", help="Where scorecards live."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Cheapest tier the evidence proves sufficient (T0-T3), with the reason."""
        from apiforge.capabilities.scorecard import load_scorecards
        from apiforge.cli import _echo_json, _run
        from apiforge.economy.providers import decide_tier

        _echo_json(
            _run(
                lambda: decide_tier(
                    capability, risk, family=family, scorecards=load_scorecards(root)
                )
            ),
            detail_level,
        )

    @agentops_app.command("prompt")
    def agentops_prompt_cmd(
        capability: str = typer.Option(..., "--capability"),
        task: str = typer.Option("", "--task"),
        expertise: list[str] = typer.Option([], "--expertise"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Stable prompt prefix (hashed) and the run-specific suffix."""
        from apiforge.cli import _echo_json, _run
        from apiforge.runtime.prompting import envelope

        _echo_json(
            _run(lambda: envelope(root, capability, task=task, expertise=expertise)), detail_level
        )

    @workspace_app.command("locality")
    def workspace_locality_cmd(
        target: str = typer.Option(..., "--target", help="Repository name or id."),
        transitive: bool = typer.Option(False, "--transitive"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """Target repo first, direct neighbors next, transitive only on request."""
        from apiforge.cli import _echo_json, _run
        from apiforge.workspace.locality import plan_locality

        _echo_json(_run(lambda: plan_locality(root, target, transitive=transitive)), detail_level)


__all__ = ["register"]
