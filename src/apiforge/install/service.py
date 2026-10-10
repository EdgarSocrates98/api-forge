"""Portable install lifecycle for API Forge — the ``forge/*`` contract v1
implemented over the vendored installkit (``apiforge._installkit``).

O motor generico (Ledger, lock, receipts, marker blocks, ``.mcp.json``
managed key, resolve_scope, drift, handshake MCP) vive no installkit; aqui
ficam a ForgeSpec do API Forge e os wrappers tipados que a CLI chama.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from apiforge import __version__
from apiforge import _installkit as kit
from apiforge.install import render

FORGE_ID = "api-forge"
STATE_DIR = ".apiforge/install"
PROFILES: tuple[str, ...] = ("minimal", "recommended", "full")
SCOPES: tuple[str, ...] = ("project", "workspace", "user")


def _spec() -> kit.ForgeSpec:
    return kit.ForgeSpec(
        forge_id=FORGE_ID,
        package="apiforge",
        distribution="apiforge",
        cli_name="apiforge",
        python_spec=">=3.12,<3.13",
        state_dir=STATE_DIR,
        mcp_command=("apiforge-mcp",),
        mcp_server_name="apiforge",
        mcp_verify_tool="portable_status",
        version_cmd=("--version",),
        render_assets=_render_for,
        marker_files=("AGENTS.md", "CLAUDE.md"),
        marker_body=(
            "**API Forge** esta instalado neste projeto.\n\n"
            "- MCP server: `apiforge` (chave gerenciada em `.mcp.json`)\n"
            "- Skills/agents: mirrors gerenciados nos diretorios de host\n"
            "- Ciclo de vida: `apiforge install status|doctor|repair|uninstall`\n\n"
            "Conteudo entre os marcadores `api-forge:managed` e gerenciado; "
            "o que estiver fora e do usuario."
        ),
        user_state_dir="~/.apiforge",
    )


def _render_for(ctx: kit.InstallContext) -> dict[str, bytes]:
    kinds = set(kit.asset_kinds_for(ctx))
    return render.render(
        ctx.hosts, skills="skill" in kinds, agents="agent" in kinds)


def _ctx(scope: str, root: Path | None, hosts: tuple[str, ...],
         profile: str, dry_run: bool, cwd: Path | None = None,
         components: tuple[str, ...] | None = None) -> kit.InstallContext:
    spec = _spec()
    base = Path(cwd or Path.cwd())
    target = kit.resolve_scope(spec, scope, base, root)
    return kit.InstallContext(
        spec=spec, scope=scope, root=target,
        state_dir=kit.state_dir_for(spec, scope, target),
        profile=profile, hosts=hosts, dry_run=dry_run,
        options=kit.component_options(profile, components))


def _hosts(host: str) -> tuple[str, ...]:
    """``all`` → todos; ``none``/vazio → opt-out explícito (nunca todos);
    nome único ou csv → subconjunto validado (GAP-003)."""
    if host == "all":
        return render.HOSTS
    if not host or host == "none":
        return ()
    nomes = [h.strip() for h in host.split(",") if h.strip()]
    desconhecidos = [h for h in nomes if h not in render.HOSTS]
    if desconhecidos:
        raise kit.InstallError(
            kit.E_HOST,
            f"host {desconhecidos[0]!r}; conhecidos: {list(render.HOSTS)} + all,none")
    return tuple(dict.fromkeys(nomes))


def install(host: str = "all", *, scope: str = "project",
            root: Path | None = None, profile: str = "recommended",
            yes: bool = False, dry_run: bool = False,
            components: tuple[str, ...] | None = None) -> dict[str, Any]:
    """Aplica a instalacao no alvo resolvido. Sem ``yes`` nem ``dry_run``
    a escrita e recusada — o plano e o contrato."""
    if profile not in PROFILES:
        raise kit.InstallError(kit.E_PROFILE, f"profile {profile!r}; {PROFILES}")
    ctx = _ctx(scope, root, _hosts(host), profile, dry_run, components=components)
    state = ctx.state_dir
    with kit.acquire_lock(state):
        receipt = kit.apply_install(ctx, approved=yes)
    if not dry_run and receipt.get("status") == "completed":
        _write_receipt(state, receipt)
        _register(ctx)
    return receipt


def status(*, scope: str = "project", root: Path | None = None) -> dict[str, Any]:
    ctx = _ctx(scope, root, (), "recommended", dry_run=True)
    return kit.status(ctx)


def doctor(*, scope: str = "project", root: Path | None = None) -> dict[str, Any]:
    ctx = _ctx(scope, root, (), "recommended", dry_run=True)
    import importlib.util
    if importlib.util.find_spec("mcp") is None:
        doc = kit.doctor(ctx)
        doc["checks"] = [
            c if c["id"] != "mcp-handshake" else
            {**c, "status": "UNVERIFIED",
             "detail": "extra 'mcp' nao instalada — handshake nao testado"}
            for c in doc["checks"]
        ]
        if not any(c["status"] == "FAIL" for c in doc["checks"]):
            doc["status"] = ("healthy" if doc["status"] != "broken"
                             else doc["status"])
        return doc
    return kit.doctor(ctx)


def repair(*, scope: str = "project", root: Path | None = None,
           dry_run: bool = False) -> dict[str, Any]:
    ctx = _ctx(scope, root, render.HOSTS, "full", dry_run)
    if dry_run:
        return kit.status(ctx)
    with kit.acquire_lock(ctx.state_dir):
        return kit.repair(ctx)


def uninstall(*, scope: str = "project", root: Path | None = None,
              purge: bool = False, dry_run: bool = False) -> dict[str, Any]:
    ctx = _ctx(scope, root, (), "recommended", dry_run)
    if dry_run:
        st = kit.status(ctx)
        return {"schema": kit.SCHEMA_RECEIPT, "forge_id": FORGE_ID,
                "operation": "uninstall", "scope": scope, "dry_run": True,
                "would_remove": st.get("drift", {}),
                "status": "planned",
                "verification": {"status": "UNVERIFIED"},
                "created_at": kit._utc_now()}
    with kit.acquire_lock(ctx.state_dir):
        return kit.uninstall(ctx, purge_state=purge)


def update(*, to: str | None = None, repo: Path | None = None,
           dry_run: bool = False) -> dict[str, Any]:
    """Atualiza o runtime instalado pelo bootstrap; ``to`` e sempre pinned."""
    if to == "latest":
        return _failed("version", "'latest' nunca e instalavel")
    manifest = _installation_manifest()
    src = repo or (Path(p) if (p := (manifest.get("source") or {}).get("path")) else None)
    if src is None or not src.exists():
        return _failed("source",
                       "sem checkout registrado — instale pelo setup", "BLOCKED")
    venv = manifest.get("venv")
    if not venv:
        return _failed("source",
                       "sem venv registrada; rode scripts/forge_bootstrap.py")
    venv_py = Path(venv) / ("Scripts/python.exe" if sys.platform == "win32"
                            else "bin/python")
    if not venv_py.exists():
        return _failed("venv", f"venv {venv} incompleta")
    cmd = [str(venv_py), "-m", "pip", "install", "--upgrade", str(src)]
    if dry_run:
        return _receipt("update", [{"id": "pip", "status": "UNVERIFIED",
                                    "detail": " ".join(cmd)}], "planned")
    import subprocess
    proc = subprocess.run(  # venv python + fixed pip args
        cmd, capture_output=True, text=True, timeout=900, check=False)
    checks = [{"id": "pip",
               "status": "PASS" if proc.returncode == 0 else "FAIL",
               "detail": (proc.stdout or proc.stderr)[-300:]}]
    return _receipt("update", checks,
                    "completed" if proc.returncode == 0 else "failed")


def mcp_verify() -> dict[str, Any]:
    return kit.mcp_verify(_spec())


# --------------------------------------------------------------------------

def _receipt(operation: str, checks: list[dict[str, Any]],
             status: str) -> dict[str, Any]:
    return {
        "schema": kit.SCHEMA_RECEIPT, "forge_id": FORGE_ID,
        "operation": operation, "managed_files": [], "checks": checks,
        "verification": {"status": "PASS" if all(
            c["status"] in ("PASS", "NOT_APPLICABLE", "UNVERIFIED")
            for c in checks) else "FAIL"},
        "status": status, "created_at": kit._utc_now(),
        "created_by": f"apiforge/{__version__}",
    }


def _failed(check_id: str, detail: str, status: str = "FAIL") -> dict[str, Any]:
    return _receipt("update", [{"id": check_id, "status": status,
                                "detail": detail}], "failed")


def _write_receipt(state: Path, receipt: dict[str, Any]) -> None:
    kit._write_receipt(state, receipt)


def _installation_manifest() -> dict[str, Any]:
    path = kit.installations_dir() / f"{FORGE_ID}.json"
    doc = kit._load_json(path, None)
    return doc if isinstance(doc, dict) else {}


def _register(ctx: kit.InstallContext) -> None:
    """Atualiza ``~/.forge/installations/api-forge.json`` sem perder o que o
    bootstrap registrou (venv, source); sem bootstrap, grava um minimo."""
    path = kit.installations_dir() / f"{FORGE_ID}.json"
    existing = kit._load_json(path, None)
    doc = dict(existing) if isinstance(existing, dict) else {}
    doc.update({
        "schema": kit.SCHEMA_MANIFEST, "forge_id": FORGE_ID,
        "package": "apiforge", "distribution": "apiforge",
        "cli": {"name": "apiforge", "version_cmd": ["apiforge", "--version"]},
        "version": __version__,
        "updated_at": kit._utc_now(),
        "installed_at": doc.get("installed_at", kit._utc_now()),
        "installed_by": doc.get("installed_by",
                                {"agent": "apiforge-cli",
                                 "version": __version__}),
        "source": doc.get("source", {"kind": "project-install",
                                     "path": str(ctx.root)}),
    })
    doc.setdefault("install_root", str(kit.installs_root() / FORGE_ID))
    doc.setdefault("mcp", {"server_name": "apiforge",
                           "command": ["apiforge-mcp"], "verified": False})
    kit.register_installation(doc)


__all__ = ["PROFILES", "SCOPES", "doctor", "install", "mcp_verify",
           "repair", "status", "uninstall", "update"]
