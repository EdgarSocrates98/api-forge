"""``apiforge portal`` — the optional local web UI over the real services.

The portal binds 127.0.0.1 with a session token, serves the vendored SPA
and maps ``forge/PortalApi/1`` operations onto ``apiforge.install.service``,
``integrations.hosts``, ``application.analyze`` and ``graphview``. It is a
view over the same engine — never a second implementation, and it never
runs inside the MCP flow.
"""
from __future__ import annotations

import json
import sys
import webbrowser
from pathlib import Path

import typer


def _portal(
    no_browser: bool = typer.Option(
        False, "--no-browser",
        help="Only print the session URL — SSH/headless or manual open.",
    ),
    port: int = typer.Option(
        0, "--port", help="Fixed port (default: a free port of the system).",
    ),
    root: Path = typer.Option(
        Path("."), "--root", help="Workspace to inspect (default: cwd).",
    ),
) -> None:
    """Open the API Forge local web portal (127.0.0.1, session token).

    Why: the §portal surface — one local UI with the installation
    dashboard, AI hosts, MCP handshake, skills/agents catalogs, tasks
    (incl. real API analysis), graph and docs, reusing the same engine
    and receipts as the CLI. When to use: to install and verify the
    forge, configure Claude/Devin/Codex, run the first analysis — or to
    audit state without learning verb flags. Optional: CLI, TUI and MCP
    keep working without it, and it never runs during MCP use.
    """
    from apiforge import _forge_portal as fp
    from apiforge.portal_adapter import ApiForgePortal

    adapter = ApiForgePortal(root.resolve())
    if adapter.assets_dir is None:
        typer.echo(json.dumps({
            "refusal": "AF-PORTAL-NO-ASSETS",
            "detail": (
                "portal assets not vendored — the clone needs "
                "`portal/assets/` (run `python scripts/vendor.py` in "
                "forge-portal); a pip install carries them in "
                "apiforge/portal_assets"
            ),
        }))
        raise typer.Exit(1)
    server = fp.PortalServer(adapter, port=port, quiet=True)
    url = server.url
    typer.echo(json.dumps({
        "url": url,
        "note": "portal is optional — CLI/TUI/MCP keep working without it",
    }))
    if not no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


def register(app: typer.Typer) -> None:
    app.command("portal")(_portal)


if __name__ == "__main__":
    sys.exit(_portal())
