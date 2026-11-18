"""Portable install lifecycle for API Forge — the ``forge/*`` contract v1
implemented over the vendored installkit (``apiforge._installkit``).

O motor generico (Ledger, lock, receipts, marker blocks, ``.mcp.json``
managed key, resolve_scope, drift, handshake MCP) vive no installkit; aqui
ficam a ForgeSpec do API Forge e os wrappers tipados que a CLI chama.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from apiforge import __version__, discovery_ops
from apiforge import _forgecontext as fctx
from apiforge import _installkit as kit
from apiforge.install import render

FORGE_ID = "api-forge"
STATE_DIR = ".apiforge/install"
PROFILES: tuple[str, ...] = ("minimal", "recommended", "full")
GATEWAY_PROFILES: tuple[str, ...] = ("economy", "balanced", "deep")
SCOPES: tuple[str, ...] = ("project", "workspace", "user")

# --------------------------------------------------------------------------
# Matriz de profiles (install-2.1)
#
# `--profile` seleciona CONJUNTOS DE COMPONENTES — e nada mais. Nao ha
# diferenca de conteudo dentro de um kind nem de "profundidade": hoje
# `recommended` e `full` instalam o MESMO conjunto de arquivos; `full` e o
# slot reservado a defaults mais pesados (componentes opcionais como
# `tui`/`graph-studio`) quando entrarem no pacote — declarar diferenca de
# disco entre eles seria inventar. `--components` sobrescreve por kind.
#
# `--gateway-profile` e uma dimensao ORTOGONAL: escolhe so o `--surface`
# embutido no argv MCP gravado em `.mcp.json` — `economy`/`balanced`
# ligam `--surface compact` (seis gateways), `deep` liga `--surface full`.
# Nao mexe em nenhum asset.
# --------------------------------------------------------------------------

# Os kinds de asset (`kit.COMPONENT_KINDS` + core) que cada `--profile`
# habilita — espelha `kit.profile_asset_kinds`, tornado dado declarado.
PROFILE_COMPONENTS: dict[str, tuple[str, ...]] = {
    "minimal": ("config", "mcp", "marker", "state"),
    "recommended": (
        "config",
        "mcp",
        "marker",
        "state",
        "skill",
        "agent",
        "knowledge",
        "rules",
        "evals",
    ),
    "full": (
        "config",
        "mcp",
        "marker",
        "state",
        "skill",
        "agent",
        "knowledge",
        "rules",
        "evals",
    ),
}

# `--gateway-profile` → superficie MCP escrita no argv de `.mcp.json`.
_GATEWAY_SURFACE: dict[str, str] = {
    "economy": "compact",
    "balanced": "compact",
    "deep": "full",
}


def _mcp_command(gateway_profile: str | None) -> tuple[str, ...]:
    """O argv `apiforge-mcp` do spec — o `--surface` do gateway-profile
    gravado, ou o default full-surface (sem flag) para instalacoes
    anteriores a flag e para sondas doctor/verify."""
    surface = _GATEWAY_SURFACE.get(gateway_profile or "")
    return ("apiforge-mcp", "--surface", surface) if surface else ("apiforge-mcp",)


def _spec(gateway_profile: str | None = None) -> kit.ForgeSpec:
    return kit.ForgeSpec(
        forge_id=FORGE_ID,
        package="apiforge",
        distribution="apiforge-af",
        cli_name="apiforge",
        python_spec=">=3.12",
        state_dir=STATE_DIR,
        mcp_command=_mcp_command(gateway_profile),
        mcp_server_name="apiforge",
        mcp_verify_tool="portable_status",
        version_cmd=("--version",),
        render_assets=_render_for,
        # Consumer docs (AGENTS.md/CLAUDE.md/AGENT_PROTOCOL.md) sao da camada
        # forge_context — blocos `forge:<forge-id>` + protocolo consolidado,
        # nao markers `api-forge:managed` (lf-0036). O ledger generico nao
        # escreve mais esses arquivos.
        marker_files=(),
        marker_body="",
        user_state_dir="~/.apiforge",
    )


def _render_for(ctx: kit.InstallContext) -> dict[str, bytes]:
    kinds = set(kit.asset_kinds_for(ctx))
    return render.render(ctx.hosts, skills="skill" in kinds, agents="agent" in kinds)


def _recorded_gateway_profile(state_dir: Path) -> str | None:
    """O `--gateway-profile` que o ultimo install persistiu em
    `components.json` (`options["execution_profile"]`); None para
    instalacoes anteriores a flag — o spec delas e o argv bare."""
    comps = kit.load_components(state_dir)
    gp = comps.get("execution_profile")
    return gp if isinstance(gp, str) and gp in _GATEWAY_SURFACE else None


def _ctx(
    scope: str,
    root: Path | None,
    hosts: tuple[str, ...],
    profile: str,
    dry_run: bool,
    cwd: Path | None = None,
    components: tuple[str, ...] | None = None,
    gateway_profile: str | None = None,
) -> kit.InstallContext:
    base = Path(cwd or Path.cwd())
    target = kit.resolve_scope(_spec(), scope, base, root)
    state_dir = kit.state_dir_for(_spec(), scope, target)
    # O spec do caminho de leitura/repair (sem profile explicito) tem de
    # reproduzir o argv que o install gravou — o execution_profile gravado
    # e a fonte; sem ele (install pre-flag) o argv bare full-surface.
    spec = _spec(
        gateway_profile if gateway_profile is not None else _recorded_gateway_profile(state_dir)
    )
    options = kit.component_options(profile, components)
    if components is None:
        # PROFILE_COMPONENTS e a fonte declarada do mapa profile→kinds —
        # os mesmos conjuntos de `kit.profile_asset_kinds`, como dado.
        options["asset_kinds"] = list(PROFILE_COMPONENTS[profile])
    if gateway_profile is not None:
        options["execution_profile"] = gateway_profile
    return kit.InstallContext(
        spec=spec,
        scope=scope,
        root=target,
        state_dir=state_dir,
        profile=profile,
        hosts=hosts,
        dry_run=dry_run,
        options=options,
    )


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
            kit.E_HOST, f"host {desconhecidos[0]!r}; conhecidos: {list(render.HOSTS)} + all,none"
        )
    return tuple(dict.fromkeys(nomes))


def install(
    host: str = "all",
    *,
    scope: str = "project",
    root: Path | None = None,
    profile: str = "recommended",
    yes: bool = False,
    dry_run: bool = False,
    components: tuple[str, ...] | None = None,
    gateway_profile: str = "balanced",
) -> dict[str, Any]:
    """Aplica a instalacao no alvo resolvido. Sem ``yes`` nem ``dry_run``
    a escrita e recusada — o plano e o contrato."""
    if profile not in PROFILES:
        raise kit.InstallError(kit.E_PROFILE, f"profile {profile!r}; {PROFILES}")
    if gateway_profile not in GATEWAY_PROFILES:
        raise kit.InstallError(
            kit.E_PROFILE,
            f"gateway_profile {gateway_profile!r}; {GATEWAY_PROFILES}",
        )
    ctx = _ctx(
        scope,
        root,
        _hosts(host),
        profile,
        dry_run,
        components=components,
        gateway_profile=gateway_profile,
    )
    state = ctx.state_dir
    with kit.acquire_lock(state):
        receipt = kit.apply_install(ctx, approved=yes)
        _migrate_knowledge_namespace(ctx, receipt)
    if not dry_run and receipt.get("status") == "completed":
        _register_context(ctx, receipt)
        _drop_stale_doc_entries(ctx)
        _write_receipt(state, receipt)
        _write_workspace_doc(ctx, receipt)
        _register(ctx)
    return receipt


def status(*, scope: str = "project", root: Path | None = None) -> dict[str, Any]:
    ctx = _ctx(scope, root, (), "recommended", dry_run=True)
    return kit.status(ctx)


def doctor(*, scope: str = "project", root: Path | None = None) -> dict[str, Any]:
    ctx = _ctx(scope, root, (), "recommended", dry_run=True)
    doc = kit.doctor(ctx)
    # A sonda de handshake vai na superficie FULL, nao no argv gravado:
    # `portable_status` nao e exposta na superficie compact, entao um
    # install economy/balanced reportaria FAIL falso. Drift e mcp-config
    # seguem fieis ao gateway-profile gravado (spec do ctx). Mesma regra
    # do `install verify` e do lifecycle de referencia.
    import importlib.util

    if importlib.util.find_spec("mcp") is None:
        probe: dict[str, Any] = {
            "id": "mcp-handshake",
            "status": "UNVERIFIED",
            "detail": "extra 'mcp' nao instalada — handshake nao testado",
        }
        invoke = None
    else:
        probe = kit.mcp_verify(_spec())
        invoke = probe.get("invoke")
    checks: list[dict[str, Any]] = []
    for c in doc["checks"]:
        if c["id"] == "mcp-handshake":
            checks.append(probe)
        elif c["id"] == "mcp-invoke":
            if isinstance(invoke, dict):
                checks.append(
                    {
                        "id": "mcp-invoke",
                        "status": invoke["status"],
                        "detail": f"{invoke['tool']}: {invoke['detail']}",
                        "repairable": False,
                    }
                )
        else:
            checks.append(c)
    doc["checks"] = checks
    contexto = doc.get("context")
    if isinstance(contexto, dict):
        contexto["tools_exposed"] = (
            len(probe["tools"]) if isinstance(probe.get("tools"), list) else None
        )
    installed = bool(isinstance(contexto, dict) and contexto.get("managed_entries"))
    if any(c["status"] == "FAIL" for c in checks):
        doc["status"] = "degraded" if installed else "broken"
    elif not installed:
        doc["status"] = "unverified"
    else:
        doc["status"] = "healthy"
    return doc


def repair(
    *, scope: str = "project", root: Path | None = None, dry_run: bool = False
) -> dict[str, Any]:
    ctx = _ctx(scope, root, render.HOSTS, "full", dry_run)
    if dry_run:
        return kit.status(ctx)
    with kit.acquire_lock(ctx.state_dir):
        receipt = kit.repair(ctx)
        # Registry de contexto (recuperacao §9.2): redo de journal de
        # transacao, reclaim de lock velho, rebuild de registry+ROUTING.md
        # — so quando `.forge/context/` ja existe (repair nunca cria
        # residuo num root pristino).
        if (ctx.root / fctx.CONTEXT_DIR).exists():
            try:
                out_ctx = fctx.repair_context(ctx.root)
                receipt["repaired"].extend(f"context:{w}" for w in out_ctx["written"])
                rec = out_ctx.get("recovered")
                receipt.setdefault("checks", []).append(
                    {
                        "id": "context-registry",
                        "status": "PASS",
                        "detail": (
                            f"{out_ctx['status']} ({len(out_ctx['written'])} writes)"
                            + (f"; recovered {rec['op']}:{rec['forge_id']}" if rec else "")
                            + ("; stale lock reclaimed" if out_ctx.get("lock_recovered") else "")
                        ),
                    }
                )
            except fctx.ContextError as exc:
                receipt["skipped"].append(f"context:{exc.kind}")
                receipt.setdefault("checks", []).append(
                    {
                        "id": "context-registry",
                        "status": "BLOCKED",
                        "detail": f"{exc.kind}: {exc.detail}",
                    }
                )
        # Consumer docs: re-assert dos blocos `forge:*` a partir dos
        # manifests em `.forge/context/`; recusa nomeada vira check.
        try:
            out_docs = fctx.repair_docs(ctx.root, legacy_tags=_LEGACY_DOC_TAGS)
            receipt["repaired"].extend(f"docs:{w}" for w in out_docs["written"])
            receipt.setdefault("checks", []).append(
                {
                    "id": "consumer-docs",
                    "status": "PASS",
                    "detail": f"{out_docs['status']} ({len(out_docs['written'])} writes)",
                }
            )
        except fctx.ContextError as exc:
            receipt["skipped"].append(f"docs:{exc.kind}")
            receipt.setdefault("checks", []).append(
                {"id": "consumer-docs", "status": "BLOCKED", "detail": f"{exc.kind}: {exc.detail}"}
            )
        return receipt


def uninstall(
    *, scope: str = "project", root: Path | None = None, purge: bool = False, dry_run: bool = False
) -> dict[str, Any]:
    ctx = _ctx(scope, root, (), "recommended", dry_run)
    if dry_run:
        st = kit.status(ctx)
        return {
            "schema": kit.SCHEMA_RECEIPT,
            "forge_id": FORGE_ID,
            "operation": "uninstall",
            "scope": scope,
            "dry_run": True,
            "would_remove": st.get("drift", {}),
            "status": "planned",
            "verification": {"status": "UNVERIFIED"},
            "created_at": kit._utc_now(),
        }
    with kit.acquire_lock(ctx.state_dir):
        receipt = kit.uninstall(ctx, purge_state=purge)
        if _docs_leftovers(ctx.root):
            checks = _unregister_context(ctx.root)
            receipt.setdefault("checks", []).extend(checks)
            # BLOCKED num componente mandatório não sai exit 0.
            if any(c.get("status") == "BLOCKED" for c in checks):
                receipt["status"] = "failed"
            if not purge:
                # kit.uninstall persistiu o receipt antes do unregister —
                # regrava para refletir checks/status finais no arquivo.
                _write_receipt(ctx.state_dir, receipt)
        return receipt


def update(
    *, to: str | None = None, repo: Path | None = None, dry_run: bool = False
) -> dict[str, Any]:
    """Atualiza o runtime instalado pelo bootstrap; ``to`` e sempre pinned."""
    if to == "latest":
        return _failed("version", "'latest' nunca e instalavel")
    manifest = _installation_manifest()
    src = repo or (Path(p) if (p := (manifest.get("source") or {}).get("path")) else None)
    if src is None or not src.exists():
        return _failed("source", "sem checkout registrado — instale pelo setup", "BLOCKED")
    venv = manifest.get("venv")
    if not venv:
        return _failed("source", "sem venv registrada; rode scripts/forge_bootstrap.py")
    venv_py = Path(venv) / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not venv_py.exists():
        return _failed("venv", f"venv {venv} incompleta")
    cmd = [str(venv_py), "-m", "pip", "install", "--upgrade", str(src)]
    if dry_run:
        return _receipt(
            "update", [{"id": "pip", "status": "UNVERIFIED", "detail": " ".join(cmd)}], "planned"
        )
    import subprocess

    proc = subprocess.run(  # venv python + fixed pip args
        cmd, capture_output=True, text=True, timeout=900, check=False
    )
    checks = [
        {
            "id": "pip",
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "detail": (proc.stdout or proc.stderr)[-300:],
        }
    ]
    return _receipt("update", checks, "completed" if proc.returncode == 0 else "failed")


def mcp_verify() -> dict[str, Any]:
    return kit.mcp_verify(_spec())


def _migrate_knowledge_namespace(ctx: kit.InstallContext, receipt: dict[str, Any]) -> None:
    """install-2.1: stubs `knowledge/<rel>` de installs antigos migram para
    `knowledge/api-forge/<rel>` (`render.KNOWLEDGE_NAMESPACE`).

    Migracao honesta sobre o ledger: entrada managed cujo sha em disco
    ainda e o registrado era nossa — sai do disco e do ledger (o stub
    namespacado a substitui). Arquivo editado pelo usuario fica, com
    nota nomeada — posse liberada, conteudo nunca apagado. Arquivo que
    nunca foi nosso (sem entrada managed — outra forja ou do usuario)
    nao e tocado. No dry-run nada e escrito: a migracao vira
    `planned_files` com `action="removed"`.
    """
    ns = f"knowledge/{render.KNOWLEDGE_NAMESPACE}/"
    ledger = kit.Ledger.load(ctx.state_dir)
    files_key = "planned_files" if ctx.dry_run else "managed_files"
    removed: list[str] = []
    preserved = 0
    for rel, entry in sorted(ledger.entries().items()):
        if not rel.startswith("knowledge/") or rel.startswith(ns):
            continue
        if not entry.get("managed") or not kit._safe_rel(rel):
            continue  # adopted/foreign or unsafe — never ours to move
        target = ctx.root / rel
        on_disk = target.read_bytes() if target.is_file() else None
        intact = on_disk is not None and kit._sha(on_disk) == entry.get("sha256")
        if ctx.dry_run:
            action, note = (
                ("removed", f"migrates to {ns}")
                if intact
                else ("unchanged", "not intact on disk — preserved")
            )
        else:
            ledger.drop(rel)
            if intact:
                target.unlink()
                action, note = "removed", f"migrated to {ns}"
            else:
                # Ausente ou editado pelo usuario: posse liberada no
                # ledger, arquivo (se existe) preservado no disco.
                action, note = (
                    "unchanged",
                    (
                        "stale bare knowledge pointer — entry released"
                        if on_disk is None
                        else "user-modified bare knowledge pointer — preserved"
                    ),
                )
        receipt.setdefault(files_key, []).append(
            {
                "path": rel,
                "kind": "knowledge",
                "action": action,
                "sha256": entry.get("sha256"),
                "note": note,
            }
        )
        if action == "removed":
            removed.append(rel)
        else:
            preserved += 1
    total = len(removed) + preserved
    if not total:
        return
    if not ctx.dry_run:
        kit._prune_empty_dirs(ctx.root, removed)
        ledger.save()
    receipt.setdefault("checks", []).append(
        {
            "id": "knowledge-namespace",
            "status": "PASS",
            "detail": (
                f"{len(removed)} stale knowledge pointers migrated to {ns}; "
                f"{preserved} preserved (foreign or user-modified)"
            ),
        }
    )


# --------------------------------------------------------------------------


def _receipt(operation: str, checks: list[dict[str, Any]], status: str) -> dict[str, Any]:
    return {
        "schema": kit.SCHEMA_RECEIPT,
        "forge_id": FORGE_ID,
        "operation": operation,
        "managed_files": [],
        "checks": checks,
        "verification": {
            "status": "PASS"
            if all(c["status"] in ("PASS", "NOT_APPLICABLE", "UNVERIFIED") for c in checks)
            else "FAIL"
        },
        "status": status,
        "created_at": kit._utc_now(),
        "created_by": f"apiforge/{__version__}",
    }


def _failed(check_id: str, detail: str, status: str = "FAIL") -> dict[str, Any]:
    return _receipt("update", [{"id": check_id, "status": status, "detail": detail}], "failed")


def _write_receipt(state: Path, receipt: dict[str, Any]) -> None:
    kit._write_receipt(state, receipt)


def _write_workspace_doc(ctx: kit.InstallContext, receipt: dict[str, Any]) -> None:
    """`forge/WorkspaceInstall/v1` do escopo workspace — o documento que o
    plano consolidado le para saber que este root e um workspace deste
    forge, com o receipt da instalacao que o gravou."""
    if ctx.scope != "workspace":
        return
    doc = {
        "schema": kit.SCHEMA_WORKSPACE,
        "workspace_root": str(ctx.root),
        "projects": [
            {
                "path": str(ctx.root),
                "forge_id": FORGE_ID,
                "receipt_id": receipt["receipt_id"],
                "installed_at": receipt["created_at"],
            }
        ],
        "created_at": receipt["created_at"],
        "updated_at": receipt["created_at"],
    }
    path = ctx.state_dir / "workspace-install.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
    doc.update(
        {
            "schema": kit.SCHEMA_MANIFEST,
            "forge_id": FORGE_ID,
            "package": "apiforge",
            "distribution": "apiforge",
            "cli": {"name": "apiforge", "version_cmd": ["apiforge", "--version"]},
            "version": __version__,
            "updated_at": kit._utc_now(),
            "installed_at": doc.get("installed_at", kit._utc_now()),
            "installed_by": doc.get(
                "installed_by", {"agent": "apiforge-cli", "version": __version__}
            ),
            "source": doc.get("source", {"kind": "project-install", "path": str(ctx.root)}),
        }
    )
    doc.setdefault("install_root", str(kit.installs_root() / FORGE_ID))
    mcp_doc = doc.setdefault(
        "mcp",
        {"server_name": "apiforge", "command": ["apiforge-mcp"], "verified": False},
    )
    if isinstance(mcp_doc, dict):
        # O orquestrador descobre a tool de verificacao aqui — setdefault
        # preserva um `verify_tool` ja registrado pelo bootstrap.
        mcp_doc.setdefault("verify_tool", "portable_status")
    doc.update(_declared_install_fields())
    kit.register_installation(doc)


def _declared_install_fields() -> dict[str, Any]:
    """As declaracoes install-2.1 do `forge.json` deste forge — copiadas
    verbatim para o manifesto registrado, nunca fabricadas (espelha o
    passo `register` do `forge_bootstrap`):

    - ``installation_kind``: ``content``|``service``|``control-tool`` —
      a classe que o plano consolidado usa na ordenacao estavel.
    - ``install``: a superficie declarada (operations/flags/hosts/scopes/
      profiles/approval) — o argv builder do orquestrador so envia o que
      esta declarado; ausente, o manifesto fica no default v1.
    - ``depends_on``: forge_ids que devem instalar antes — declarado
      mesmo quando vazio (``[]``): o plano consolidado le a presenca da
      chave como declaracao explicita, nao como ausencia de dado.
    """
    cfg = _bundled_json("forge.json")
    if not cfg:
        return {}
    doc: dict[str, Any] = {}
    if cfg.get("installation_kind"):
        kind = str(cfg["installation_kind"])
        if kind not in kit.INSTALLATION_KINDS:
            raise kit.InstallError(
                kit.E_UNSUPPORTED,
                f"forge.json installation_kind {kind!r} — expected {kit.INSTALLATION_KINDS}",
            )
        doc["installation_kind"] = kind
    if cfg.get("install"):
        doc["install"] = dict(cfg["install"])
    if "depends_on" in cfg:
        doc["depends_on"] = [str(d) for d in cfg["depends_on"]]
    return doc


__all__ = [
    "PROFILES",
    "SCOPES",
    "doctor",
    "install",
    "mcp_verify",
    "repair",
    "status",
    "uninstall",
    "update",
]


# --------------------------------------------------------------------------
# forge-context/v1 wiring (install-2.0 ciclo 2, the-forge ADR-0061)
# `.forge/context/` e o registry de workspace compartilhado entre forges —
# camada diferente de `~/.forge/installations/` (conta) e de
# `.apiforge/install/` (ledger). Este forge so registra e desregistra o
# proprio `forge_id`.
# --------------------------------------------------------------------------

_PKG_DIR = Path(__file__).resolve().parents[1]
_REPO_DIR = _PKG_DIR.parent.parent  # src/apiforge -> repo root

# Markers de geracoes anteriores (`api-forge:managed:begin` do installkit
# generico); `install_docs` os remove ao convergir para `forge:<tag>`.
_LEGACY_DOC_TAGS: tuple[str, ...] = ("api-forge:managed",)
_CONSUMER_DOCS: tuple[str, ...] = ("AGENTS.md", "CLAUDE.md", "AGENT_PROTOCOL.md")


def _drop_stale_doc_entries(ctx: kit.InstallContext) -> None:
    """Remove entradas antigas de ledger para os consumer docs: os arquivos
    agora sao gerenciados pela camada forge_context (blocos `forge:*`), nao
    por hash de arquivo inteiro — conteudo do usuario fora dos marcadores
    nao e drift."""
    ledger = kit.Ledger.load(ctx.state_dir)
    changed = False
    for name in _CONSUMER_DOCS:
        if ledger.get(name) is not None:
            ledger.drop(name)
            changed = True
    if changed:
        ledger.save()


_API_DOMAINS: tuple[str, ...] = (
    "api-design",
    "api-contract",
    "api-testing",
    "api-performance",
    "api-observability",
    "api-migration",
    "data-access",
    "messaging",
)


def _mds(base: Path) -> list[str]:
    return sorted(p.stem for p in base.glob("*.md")) if base.is_dir() else []


def _bundled_json(name: str) -> dict[str, Any] | None:
    """JSON declarativo empacotado com o forge: primeiro `_data/<name>`
    dentro do pacote (wheel), depois a raiz do checkout (editable)."""
    for cand in (_PKG_DIR / "_data" / name, _REPO_DIR / name):
        data = kit._load_json(cand, None)
        if isinstance(data, dict):
            return data
    return None


def _context_manifest(ctx: kit.InstallContext) -> dict[str, Any]:
    """Manifesto forge/context/v1 montado das fontes reais: `forge.json` +
    `forge.agentic.json` no checkout e os assets que o install usou
    (`render.content_dirs`, `_data/knowledge|evals`, `rules/`)."""
    forge_json = _bundled_json("forge.json")
    agentic = _bundled_json("forge.agentic.json")

    dirs = render.content_dirs()
    skills: list[str] = []
    coordinators: list[str] = []
    executors: list[str] = []
    if dirs is not None:
        agents_src, skills_src = dirs
        skills = sorted(d.name for d in skills_src.iterdir() if d.is_dir())
        coordinators = _mds(agents_src)
        executors = _mds(agents_src / "executors")

    rules_root = _PKG_DIR / "rules"
    rule_areas = (
        sorted(p.stem for p in rules_root.glob("*.yaml"))
        + sorted(p.stem for p in (rules_root / "catalog").glob("*.yaml"))
        if rules_root.is_dir()
        else []
    )
    rule_areas = sorted(set(rule_areas))

    def _data_or_repo(name: str) -> Path | None:
        for cand in (_PKG_DIR / "_data" / name, _REPO_DIR / name):
            if cand.is_dir():
                return cand
        return None

    providers = (
        [{"id": "knowledge-base", "interface": "bundled"}]
        if _data_or_repo("knowledge") is not None
        else []
    )
    # §7.1 (lf-0038): the declared, classified eval catalog — never a bare
    # directory listing. `evals/` subdirs are corpus data; the suites that
    # run them are declared in apiforge.evals.catalog with their §7.1 kind.
    from apiforge.evals.catalog import manifest_suites

    eval_suites = manifest_suites()

    checks: list[dict[str, Any]] = [
        {
            "id": "skills-bundle",
            "status": "PASS" if skills else "UNVERIFIED",
            "detail": f"{len(skills)} skills",
        },
        {
            "id": "agent-specs",
            "status": "PASS" if coordinators else "UNVERIFIED",
            "detail": f"{len(coordinators)} coordinators, {len(executors)} executors",
        },
        {
            "id": "rules-catalog",
            "status": "PASS" if rule_areas else "UNVERIFIED",
            "detail": f"{len(rule_areas)} rule areas",
        },
    ]
    return fctx.build_manifest(
        forge_id=FORGE_ID,
        name="API Forge",
        version=__version__,
        cli="apiforge",
        package="apiforge",
        distribution="apiforge-af",
        python_spec=">=3.12",
        scope=ctx.scope,
        profile=ctx.profile,
        hosts=ctx.hosts,
        forge_json=forge_json,
        agentic=agentic,
        kind="specialist",
        domains=_API_DOMAINS,
        skills=skills,
        coordinators=coordinators,
        agents=executors,
        rule_areas=rule_areas,
        knowledge_providers=providers,
        eval_suites=eval_suites,
        protocols=(
            {"id": "forge/v1", "version": "1"},
            {"id": "forge/context/v1", "version": "1"},
            {"id": "forge/context-registry/v1", "version": "1"},
        ),
        discovery_ops=discovery_ops.ops(),
        discovery_commands=(
            *(
                c
                for c in discovery_ops.commands()
                if c["id"] != "doctor"  # `doctor` is declared below
            ),
            {
                "id": "analyze",
                "argv": ["apiforge", "analyze", "{target}"],
                "mode": "direct-capability",
                "read_only": True,
                "description": "analyze API/contract surfaces",
            },
            {
                "id": "next-step",
                "argv": ["apiforge", "next-step"],
                "mode": "specialist-workflow",
                "read_only": True,
                "description": "case-driven specialist recommendation",
            },
            {
                "id": "knowledge-select",
                "argv": ["apiforge", "knowledge", "select"],
                "mode": "direct-capability",
                "read_only": True,
                "description": "deterministic knowledge selection",
            },
            {
                "id": "doctor",
                "argv": ["apiforge", "doctor"],
                "mode": "diagnostic-only",
                "read_only": True,
                "description": "environment + installation health",
            },
        ),
        mcp={
            "server_name": "apiforge",
            "command": ["apiforge-mcp"],
            "verify_tool": "portable_status",
        },
        resources={
            "skills-bundle": {
                "kind": "bundled",
                "location": "apiforge/host_assets/skills",
                "optional": False,
            },
            "agents-bundle": {
                "kind": "bundled",
                "location": "apiforge/host_assets/agents",
                "optional": False,
            },
            "rules-catalog": {
                "kind": "bundled",
                "location": "apiforge/rules",
                "optional": False,
            },
            "knowledge-base": {
                "kind": "bundled",
                "location": "apiforge/_data/knowledge",
                "optional": True,
            },
            "evals-data": {
                "kind": "bundled",
                "location": "apiforge/_data/evals",
                "optional": True,
            },
            "install-ledger": {
                "kind": "referenced",
                "location": ".apiforge/install",
                "optional": True,
            },
        },
        mutating_verbs=(
            "install",
            "uninstall",
            "repair",
            "integrate",
            "detach",
            "collect",
            "change apply",
            "case update",
            "task run",
        ),
        requires_approval=("install", "uninstall", "integrate", "detach", "change apply"),
        offline_available=True,
        health={
            "status": ("healthy" if skills and coordinators and rule_areas else "degraded"),
            "checks": checks,
        },
        components=ctx.options or None,
        recorded_by="apiforge",
    )


def _register_context(ctx: kit.InstallContext, receipt: dict[str, Any]) -> None:
    """Grava `.forge/context/` — manifesto + entrada no registry +
    ROUTING.md. Falha vira check BLOCKED nomeado no recibo.
    ``scope=user`` tem target=``~``: ``~/.forge/`` é nível de conta —
    contexto de workspace não se escreve lá (mesma regra dos siblings)."""
    if ctx.scope == "user":
        return
    try:
        manifest = _context_manifest(ctx)
        out = fctx.install_transaction(
            ctx.root, manifest, owner=FORGE_ID, legacy_tags=_LEGACY_DOC_TAGS
        )
        receipt.setdefault("checks", []).append(
            {
                "id": "context-registry",
                "status": "PASS",
                "detail": f".forge/context {out['status']} ({len(out['written'])} writes)",
            }
        )
        docs = out["docs"]
        receipt.setdefault("checks", []).append(
            {
                "id": "consumer-docs",
                "status": "PASS",
                "detail": (
                    f"{docs['status']}: {len(docs['written'])} written, {len(docs['kept'])} kept"
                ),
            }
        )
    except fctx.ContextError as exc:
        receipt.setdefault("checks", []).append(
            {"id": "context-registry", "status": "BLOCKED", "detail": f"{exc.kind}: {exc.detail}"}
        )
        # BLOCKED num componente mandatório não pode sair exit 0 — os
        # assets foram escritos mas o contrato install-2.0 (registry +
        # consumer docs) falhou; o recibo reporta a falha.
        receipt["status"] = "failed"


def _unregister_context(root: Path) -> list[dict[str, Any]]:
    """Remove manifesto/entry/blocos `forge:*` deste forge numa UNICA
    transacao (§9.2) — só artifacts próprios."""
    try:
        out = fctx.uninstall_transaction(
            root, FORGE_ID, owner=FORGE_ID, legacy_tags=_LEGACY_DOC_TAGS
        )
        docs = out["docs"]
        return [
            {
                "id": "context-registry",
                "status": "PASS",
                "detail": f".forge/context {out['status']}",
            },
            {
                "id": "consumer-docs",
                "status": "PASS",
                "detail": f"{docs['status']}: {len(docs['written'])} changed",
            },
        ]
    except fctx.ContextError as exc:
        return [
            {
                "id": "context-registry",
                "status": "BLOCKED",
                "detail": f"{exc.kind}: {exc.detail}",
            }
        ]


def _docs_leftovers(root: Path) -> bool:
    """True quando o alvo ainda carrega resíduo forge_context — leitura sem
    lock; só um hit justifica o caminho de escrita (nunca criamos
    `.forge/context/` num root pristino)."""
    if (root / fctx.CONTEXT_DIR).exists():
        return True
    needles = (
        f"forge:{FORGE_ID}:",
        f"{fctx.DOC_TAG_ECOSYSTEM}:",
        fctx.PROTOCOL_SENTINEL,
        *_LEGACY_DOC_TAGS,
    )
    for name in _CONSUMER_DOCS:
        path = root / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(n in text for n in needles):
            return True
    return False
