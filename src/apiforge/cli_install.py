"""``apiforge install`` lifecycle commands over ``apiforge.install.service``.

`apiforge install` sem subcomando APLICA a instalacao no escopo resolvido
(projeto por padrao); os subcomandos cobrem o restante do ciclo de vida.
Sem ``--yes`` nem ``--dry-run`` a escrita e recusada — approval gate do
contrato ``forge/*``."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import typer

from apiforge import _installkit as kit
from apiforge.install import service

install_app = typer.Typer(
    name="install",
    help=(
        "Install API Forge assets into a project, workspace or the user home; "
        "manage the lifecycle (status, doctor, repair, update, uninstall)."
    ),
    invoke_without_command=True,
    no_args_is_help=False,
)

_SCOPE = typer.Option("project", "--scope", help="project|workspace|user.")
_HOST = typer.Option("all", "--host", help="claude|devin|codex|copilot|all.")
_PROFILE = typer.Option("recommended", "--profile", help="minimal|recommended|full.")
_ROOT = typer.Option(None, "--root", help="Target root (default: VCS root or cwd).")


def _emit(value: object, detail_level: str) -> None:
    """TTY humans get the Rich/kit-rendered doc; pipes and CI keep the
    JSON contract (honoring --detail-level and AF_OUTPUT)."""
    import sys

    from apiforge.cli import _echo_json, _run

    out = _run(lambda: value)
    import os

    human = sys.stdout.isatty() or bool(os.environ.get("FORGE_TEXT_OUTPUT"))
    if (
        human
        and isinstance(out, dict)
        and (str(out.get("schema", "")).startswith("forge/") or "checks" in out or "drift" in out)
    ):
        from apiforge.cli_install_pretty import render_doc
        from apiforge.core.detail import apply_detail_level

        render_doc(apply_detail_level(out, detail_level))
        return
    _echo_json(out, detail_level)


def _fail(exc: kit.InstallError) -> None:
    from apiforge.cli import _fail as _cli_fail

    doc = exc.document("api-forge")
    err = doc.get("error") or {}
    _cli_fail(
        err.get("kind", "AF-INSTALL"),
        err.get("detail", str(exc)),
        field="install",
        unlock=err.get("unlock", "run with --dry-run or --yes"),
    )


def _call(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    try:
        return fn(*args, **kwargs)
    except kit.InstallError as exc:
        _fail(exc)
        raise AssertionError("unreachable")


def _bare_install_requested(
    ctx: typer.Context,
    *,
    scope: str,
    host: str,
    profile: str,
    root: Path | None,
    yes: bool,
    dry_run: bool,
    components: str | None,
) -> bool:
    """Detect exact default invocation without guessing explicit flags."""
    if (scope, host, profile, root, yes, dry_run, components) != (
        "project", "all", "recommended", None, False, False, None
    ):
        return False
    source = getattr(ctx, "get_parameter_source", None)
    if source is None:
        return True
    return all(
        getattr(source(name), "name", "") == "DEFAULT"
        for name in ("scope", "host", "profile", "root", "yes", "dry_run", "components")
    )


@install_app.callback()
def install_apply(
    ctx: typer.Context,
    scope: str = _SCOPE,
    host: str = _HOST,
    profile: str = _PROFILE,
    root: Path | None = _ROOT,
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Explicit approval; without it only --dry-run is allowed."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan only — writes nothing."),
    components: str | None = typer.Option(
        None, "--components", help="Optional components csv: skills,agents,mcp,tui,graph-studio."
    ),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Install API Forge host assets into the resolved scope."""
    if ctx.invoked_subcommand is not None:
        return
    import sys

    comps = tuple(c.strip() for c in components.split(",") if c.strip()) if components else None
    if (
        _bare_install_requested(
            ctx,
            scope=scope,
            host=host,
            profile=profile,
            root=root,
            yes=yes,
            dry_run=dry_run,
            components=components,
        )
        and sys.stdin.isatty()
        and sys.stdout.isatty()
    ):
        from apiforge.ui.kit import UIContext
        from apiforge.ui.wizard import run_wizard

        raise typer.Exit(
            run_wizard(
                forge_name="api-forge",
                install_fn=lambda **kw: service.install(root=None, **kw),
                doctor_fn=lambda **kw: service.doctor(**kw),
                ctx=UIContext.detect(),
            )
        )
    approved = yes
    if not yes and not dry_run and sys.stdin.isatty() and sys.stdout.isatty():
        # Interactive approval: render the real plan, confirm once,
        # apply — one command instead of dry-run + apply.
        from apiforge.cli_install_pretty import render_doc

        plan = _call(
            service.install,
            host,
            scope=scope,
            root=root,
            profile=profile,
            yes=False,
            dry_run=True,
            components=comps,
        )
        render_doc(plan)
        approved = typer.confirm("Apply this plan?", default=True)
        if not approved:
            typer.echo("declined — nothing written")
            raise typer.Exit(1)
    out = _call(
        service.install,
        host,
        scope=scope,
        root=root,
        profile=profile,
        yes=approved,
        dry_run=dry_run,
        components=comps,
    )
    _emit(out, detail_level)


@install_app.command("status")
def install_status(
    scope: str = _SCOPE,
    root: Path | None = _ROOT,
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Ledger + drift + health document of the installation."""
    _emit(_call(service.status, scope=scope, root=root), detail_level)


@install_app.command("doctor")
def install_doctor(
    scope: str = _SCOPE,
    root: Path | None = _ROOT,
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Deep installation health: ledger, drift, mcp config, handshake."""
    _emit(_call(service.doctor, scope=scope, root=root), detail_level)


@install_app.command("repair")
def install_repair(
    scope: str = _SCOPE,
    root: Path | None = _ROOT,
    dry_run: bool = typer.Option(False, "--dry-run"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Rewrite managed assets that went missing or drifted."""
    _emit(_call(service.repair, scope=scope, root=root, dry_run=dry_run), detail_level)


@install_app.command("update")
def install_update(
    to: str | None = typer.Option(None, "--to", help="Pinned target version (never 'latest')."),
    repo: Path | None = typer.Option(None, "--repo", help="Checkout to install/upgrade from."),
    dry_run: bool = typer.Option(False, "--dry-run"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Upgrade the bootstrap-installed runtime."""
    _emit(_call(service.update, to=to, repo=repo, dry_run=dry_run), detail_level)


@install_app.command("uninstall")
def install_uninstall(
    scope: str = _SCOPE,
    root: Path | None = _ROOT,
    purge: bool = typer.Option(
        False, "--purge", help="Also delete the state dir .apiforge/install."
    ),
    dry_run: bool = typer.Option(False, "--dry-run"),
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Remove only what the ledger declares as managed."""
    _emit(
        _call(service.uninstall, scope=scope, root=root, purge=purge, dry_run=dry_run), detail_level
    )


@install_app.command("verify")
def install_verify(
    detail_level: str = typer.Option("normal", "--detail-level"),
) -> None:
    """Real JSON-RPC handshake: initialize + tools/list on the MCP server."""
    _emit(service.mcp_verify(), detail_level)


def register(app: typer.Typer) -> None:
    app.add_typer(install_app)


__all__ = ["install_app", "register"]
