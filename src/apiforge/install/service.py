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

from apiforge import __version__, discovery_ops
from apiforge import _forgecontext as fctx
from apiforge import _installkit as kit
from apiforge.install import render

FORGE_ID = "api-forge"
STATE_DIR = ".apiforge/install"
PROFILES: tuple[str, ...] = ("minimal", "recommended", "full")
GATEWAY_PROFILES: tuple[str, ...] = ("economy", "balanced", "deep")
SCOPES: tuple[str, ...] = ("project", "workspace", "user")


def _spec() -> kit.ForgeSpec:
    return kit.ForgeSpec(
        forge_id=FORGE_ID,
        package="apiforge",
        distribution="apiforge-af",
        cli_name="apiforge",
        python_spec=">=3.12",
        state_dir=STATE_DIR,
        mcp_command=("apiforge-mcp",),
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


def _ctx(
    scope: str,
    root: Path | None,
    hosts: tuple[str, ...],
    profile: str,
    dry_run: bool,
    cwd: Path | None = None,
    components: tuple[str, ...] | None = None,
    gateway_profile: str = "balanced",
) -> kit.InstallContext:
    spec = _spec()
    base = Path(cwd or Path.cwd())
    target = kit.resolve_scope(spec, scope, base, root)
    options = kit.component_options(profile, components)
    options["execution_profile"] = gateway_profile
    return kit.InstallContext(
        spec=spec,
        scope=scope,
        root=target,
        state_dir=kit.state_dir_for(spec, scope, target),
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
    if not dry_run and receipt.get("status") == "completed":
        _register_context(ctx, receipt)
        _drop_stale_doc_entries(ctx)
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
            c
            if c["id"] != "mcp-handshake"
            else {
                **c,
                "status": "UNVERIFIED",
                "detail": "extra 'mcp' nao instalada — handshake nao testado",
            }
            for c in doc["checks"]
        ]
        if not any(c["status"] == "FAIL" for c in doc["checks"]):
            doc["status"] = "healthy" if doc["status"] != "broken" else doc["status"]
        return doc
    return kit.doctor(ctx)


def repair(
    *, scope: str = "project", root: Path | None = None, dry_run: bool = False
) -> dict[str, Any]:
    ctx = _ctx(scope, root, render.HOSTS, "full", dry_run)
    if dry_run:
        return kit.status(ctx)
    with kit.acquire_lock(ctx.state_dir):
        receipt = kit.repair(ctx)
        # Consumer docs: re-assert dos blocos `forge:*` a partir dos
        # manifests em `.forge/context/`; recusa nomeada vira check.
        try:
            out_docs = fctx.repair_docs(
                ctx.root, legacy_tags=_LEGACY_DOC_TAGS)
            receipt["repaired"].extend(
                f"docs:{w}" for w in out_docs["written"])
            receipt.setdefault("checks", []).append(
                {"id": "consumer-docs", "status": "PASS",
                 "detail": f"{out_docs['status']} "
                           f"({len(out_docs['written'])} writes)"})
        except fctx.ContextError as exc:
            receipt["skipped"].append(f"docs:{exc.kind}")
            receipt.setdefault("checks", []).append(
                {"id": "consumer-docs", "status": "BLOCKED",
                 "detail": f"{exc.kind}: {exc.detail}"})
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
            receipt.setdefault("checks", []).append(
                _unregister_context(ctx.root))
            receipt.setdefault("checks", []).append(
                _uninstall_docs(ctx.root))
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
    doc.setdefault(
        "mcp", {"server_name": "apiforge", "command": ["apiforge-mcp"], "verified": False}
    )
    kit.register_installation(doc)


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


def _context_manifest(ctx: kit.InstallContext) -> dict[str, Any]:
    """Manifesto forge/context/v1 montado das fontes reais: `forge.json` +
    `forge.agentic.json` no checkout e os assets que o install usou
    (`render.content_dirs`, `_data/knowledge|evals`, `rules/`)."""
    def _bundled_json(name: str) -> dict[str, Any] | None:
        for cand in (_PKG_DIR / "_data" / name, _REPO_DIR / name):
            data = kit._load_json(cand, None)
            if isinstance(data, dict):
                return data
        return None

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
    evals_root = _data_or_repo("evals")
    eval_suites = (
        [
            {"id": p.name, "kind": "output-verification"}
            for p in sorted(evals_root.iterdir())
            if p.is_dir()
        ]
        if evals_root is not None
        else []
    )

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
    ROUTING.md. Falha vira check BLOCKED nomeado no recibo."""
    try:
        manifest = _context_manifest(ctx)
        out = fctx.register_forge(ctx.root, manifest, owner=FORGE_ID)
        receipt.setdefault("checks", []).append(
            {
                "id": "context-registry",
                "status": "PASS",
                "detail": f".forge/context {out['status']} ({len(out['written'])} writes)",
            }
        )
    except fctx.ContextError as exc:
        receipt.setdefault("checks", []).append(
            {"id": "context-registry", "status": "BLOCKED", "detail": f"{exc.kind}: {exc.detail}"}
        )
        return
    try:
        docs = fctx.install_docs(
            ctx.root, manifest, owner=FORGE_ID, legacy_tags=_LEGACY_DOC_TAGS
        )
        receipt.setdefault("checks", []).append(
            {
                "id": "consumer-docs",
                "status": "PASS",
                "detail": (
                    f"{docs['status']}: {len(docs['written'])} written, "
                    f"{len(docs['kept'])} kept"
                ),
            }
        )
    except fctx.ContextError as exc:
        receipt.setdefault("checks", []).append(
            {"id": "consumer-docs", "status": "BLOCKED", "detail": f"{exc.kind}: {exc.detail}"}
        )


def _unregister_context(root: Path) -> dict[str, Any]:
    """Remove somente o manifesto/entry deste forge."""
    try:
        out = fctx.unregister_forge(root, FORGE_ID, owner=FORGE_ID)
        return {
            "id": "context-registry",
            "status": "PASS",
            "detail": f".forge/context {out['status']}",
        }
    except fctx.ContextError as exc:
        return {
            "id": "context-registry",
            "status": "BLOCKED",
            "detail": f"{exc.kind}: {exc.detail}",
        }


def _docs_leftovers(root: Path) -> bool:
    """True quando o alvo ainda carrega resíduo forge_context — leitura sem
    lock; só um hit justifica o caminho de escrita (nunca criamos
    `.forge/context/` num root pristino)."""
    if (root / fctx.CONTEXT_DIR).exists():
        return True
    needles = (
        f"forge:{FORGE_ID}:", f"{fctx.DOC_TAG_ECOSYSTEM}:",
        fctx.PROTOCOL_SENTINEL, *_LEGACY_DOC_TAGS,
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


def _uninstall_docs(root: Path) -> dict[str, Any]:
    """Retira os blocos `forge:api-forge` (+ markers legados) dos consumer
    docs; roda depois do unregister para o protocolo sair sem nos."""
    try:
        out = fctx.uninstall_docs(
            root, FORGE_ID, owner=FORGE_ID, legacy_tags=_LEGACY_DOC_TAGS
        )
        return {
            "id": "consumer-docs",
            "status": "PASS",
            "detail": f"{out['status']}: {len(out['written'])} changed",
        }
    except fctx.ContextError as exc:
        return {
            "id": "consumer-docs",
            "status": "BLOCKED",
            "detail": f"{exc.kind}: {exc.detail}",
        }
