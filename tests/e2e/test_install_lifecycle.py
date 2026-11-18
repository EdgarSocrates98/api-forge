"""`apiforge install` lifecycle — project-scope write, drift, repair, revert.

Each test installs into a ``tmp_path`` project and an isolated HOME: nothing
touches the real HOME or the repository checkout's mirrors.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge import _installkit as kit
from apiforge.cli import app
from apiforge.install import service


@pytest.fixture(autouse=True)
def _home_isolado(tmp_path, monkeypatch):
    casa = tmp_path / "home_padrao"
    casa.mkdir()
    monkeypatch.setenv("HOME", str(casa))
    monkeypatch.setenv("USERPROFILE", str(casa))
    monkeypatch.setenv("APPDATA", str(casa / "AppData" / "Roaming"))


@pytest.fixture()
def projeto(tmp_path):
    p = tmp_path / "projeto"
    p.mkdir()
    (p / ".git").mkdir()
    return p


def _arquivos(base: Path) -> list[str]:
    return sorted(
        p.relative_to(base).as_posix()
        for p in base.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )


# --------------------------------------------------------------------------
# service layer
# --------------------------------------------------------------------------


def test_install_sem_aprovacao_recusa(projeto):
    with pytest.raises(kit.InstallError) as exc:
        service.install("devin", scope="project", root=projeto)
    assert exc.value.kind == kit.E_NOTAPPROVED


def test_install_devin_escreve_skills_mcp_e_marker(projeto):
    out = service.install("devin", scope="project", root=projeto, yes=True)
    assert out["status"] == "completed"
    paths = {f["path"] for f in out["managed_files"]}
    # dedup: `.agents/` é a superfície única que o Devin lê nativamente —
    # `.devin/` fica reservado a assets host-specific, sem segunda cópia.
    assert any(p.startswith(".agents/skills/") for p in paths)
    assert not any(p.startswith(".devin/skills/") for p in paths)
    mcp = json.loads((projeto / ".mcp.json").read_text(encoding="utf-8"))
    assert "apiforge" in mcp["mcpServers"]
    assert "forge:api-forge:begin" in (projeto / "AGENTS.md").read_text("utf-8")
    receipts = list((projeto / ".apiforge" / "install" / "receipts").glob("*.json"))
    assert receipts


def test_install_profile_full_inclui_agents(projeto):
    out = service.install("devin", scope="project", root=projeto, profile="full", yes=True)
    paths = {f["path"] for f in out["managed_files"]}
    # mesma dedup: agents vivem uma vez em `.agents/`, lidos pelo Devin nativo.
    assert any(p.startswith(".agents/agents/") for p in paths)
    assert not any(p.startswith(".devin/agents/") for p in paths)


def test_install_profile_minimal_sem_mirrors(projeto):
    out = service.install("devin", scope="project", root=projeto, profile="minimal", yes=True)
    assert out["status"] == "completed"
    assert not (projeto / ".devin").exists()
    assert (projeto / ".mcp.json").exists()


def test_install_nao_sobrescreve_arquivo_do_usuario(projeto):
    plano = service.install("devin", scope="project", root=projeto, dry_run=True)
    alvo_rel = next(
        f["path"]
        for f in plano["planned_files"]
        if f["path"].startswith(".agents/skills/") and f["path"].endswith("SKILL.md")
    )
    alvo = projeto / alvo_rel
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text("conteudo do usuario", encoding="utf-8")
    service.install("devin", scope="project", root=projeto, yes=True)
    assert alvo.read_text(encoding="utf-8") == "conteudo do usuario"


def test_install_dry_run_planeja_sem_escrever(projeto):
    out = service.install("devin", scope="project", root=projeto, dry_run=True)
    assert out["status"] == "planned"
    assert not (projeto / ".devin").exists()
    assert not (projeto / ".mcp.json").exists()


def test_status_e_drift(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    st = service.status(scope="project", root=projeto)
    assert st["status"] == "healthy"
    alvo = projeto / next(
        p["path"]
        for p in service.status(scope="project", root=projeto)["drift"]["modified"]
        or [{"path": ".agents/skills/api-forge-core/SKILL.md"}]
    )
    alvo = projeto / ".agents/skills/api-forge-core/SKILL.md"
    alvo.write_text("edicao manual", encoding="utf-8")
    st2 = service.status(scope="project", root=projeto)
    assert st2["status"] == "degraded"


def test_repair_restaura(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    vitima = projeto / ".agents/skills/api-forge-core/SKILL.md"
    original = vitima.read_bytes()
    vitima.unlink()
    rep = service.repair(scope="project", root=projeto)
    assert rep["status"] in ("completed", "repaired")
    assert vitima.read_bytes() == original


def test_uninstall_reverte_tudo(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    un = service.uninstall(scope="project", root=projeto, purge=True)
    assert un["status"] == "completed"
    resto = [p for p in _arquivos(projeto) if not p.startswith(".git/")]
    # `.forge/context/` e shared workspace state, nao state deste forge.
    assert sorted(resto) == [
        ".forge/context/ROUTING.md",
        ".forge/context/registry.json",
    ]


def test_uninstall_preserva_conteudo_do_usuario(projeto):
    ag = projeto / "AGENTS.md"
    ag.write_text("# Meu projeto\n", encoding="utf-8")
    service.install("devin", scope="project", root=projeto, yes=True)
    service.uninstall(scope="project", root=projeto, purge=True)
    assert ag.read_text(encoding="utf-8").strip() == "# Meu projeto"


def test_update_rejeita_latest():
    out = service.update(to="latest")
    assert out["status"] == "failed"


def test_mcp_verify_documento():
    out = service.mcp_verify()
    assert out["id"] == "mcp-handshake"
    assert out["status"] in ("PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE", "UNVERIFIED")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def test_cli_install_dry_run(projeto):
    result = CliRunner().invoke(
        app, ["install", "--host", "devin", "--root", str(projeto), "--dry-run"]
    )
    assert result.exit_code == 0, result.stdout
    doc = json.loads(result.stdout)
    assert doc["status"] == "planned"


def test_cli_install_dry_run_writes_no_economy_ledger(projeto, monkeypatch, tmp_path):
    """Regression (xpto E2E F1): a delegated `install --dry-run` runs with
    cwd = foreign workspace root — _echo_json must not create
    `.apiforge/economy.jsonl` there."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        app, ["install", "--host", "devin", "--root", str(projeto), "--dry-run"]
    )
    assert result.exit_code == 0, result.stdout
    assert not (tmp_path / ".apiforge" / "economy.jsonl").exists()
    assert not (tmp_path / ".apiforge").exists()


def test_cli_install_sem_aprovacao_falha_com_recusa(projeto):
    result = CliRunner().invoke(app, ["install", "--host", "devin", "--root", str(projeto)])
    assert result.exit_code != 0
    assert "FORGE-INSTALL-PLAN-NOT-APPROVED" in (result.stdout + (result.stderr or ""))


def test_cli_install_status(projeto):
    CliRunner().invoke(app, ["install", "--host", "devin", "--root", str(projeto), "--yes"])
    result = CliRunner().invoke(app, ["install", "status", "--root", str(projeto)])
    assert result.exit_code == 0, result.stdout
    doc = json.loads(result.stdout)
    assert doc["forge_id"] == "api-forge"
    assert doc["status"] == "healthy"


def test_cli_install_uninstall(projeto):
    CliRunner().invoke(app, ["install", "--host", "devin", "--root", str(projeto), "--yes"])
    result = CliRunner().invoke(app, ["install", "uninstall", "--root", str(projeto), "--purge"])
    assert result.exit_code == 0, result.stdout
    resto = [p for p in _arquivos(projeto) if not p.startswith(".git/")]
    # `.forge/context/` e shared workspace state, nao state deste forge.
    assert sorted(resto) == [
        ".forge/context/ROUTING.md",
        ".forge/context/registry.json",
    ]


def test_hosts_none_e_csv():
    """GAP-003: `none` nunca vira `all`; csv subconjunto e validado."""
    import pytest

    from apiforge import _installkit as kit
    from apiforge.install import render, service

    assert service._hosts("all") == render.HOSTS
    assert service._hosts("none") == ()
    assert service._hosts("") == ()
    assert service._hosts("claude") == ("claude",)
    assert set(service._hosts("claude,devin")) == {"claude", "devin"}
    with pytest.raises(kit.InstallError):
        service._hosts("nope")


# --------------------------------------------------------------------------
# forge/context/v1 — workspace registry (install-2.0 ciclo 2)
# --------------------------------------------------------------------------


def test_install_escreve_forge_context(projeto):
    from apiforge import _forgecontext as fctx

    out = service.install("devin", scope="project", root=projeto, yes=True)
    assert out["status"] == "completed"
    check = next(c for c in out["checks"] if c["id"] == "context-registry")
    assert check["status"] == "PASS"

    ctx = projeto / ".forge" / "context"
    registry = json.loads((ctx / "registry.json").read_text(encoding="utf-8"))
    assert registry["schema"] == "forge/context-registry/v1"
    entry = next(e for e in registry["forges"] if e["forge_id"] == "api-forge")
    assert entry["scope"] == "project"

    manifest = json.loads((ctx / "capabilities" / "api-forge.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "forge/context/v1"
    assert fctx.validate_manifest(manifest) == []
    assert manifest["skills"], "manifesto sem skills reais"
    assert manifest["rule_areas"], "manifesto sem rule areas"
    assert manifest["coordinators"], "manifesto sem coordinators"
    assert manifest["integrity"]["files"]["forge.json"].startswith("sha256:")

    routing = (ctx / "ROUTING.md").read_text(encoding="utf-8")
    assert "api-forge" in routing
    assert "api-design" in routing


def test_install_context_idempotente_byte_a_byte(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    ctx = projeto / ".forge" / "context"
    snap = {
        p.relative_to(ctx).as_posix(): p.read_bytes() for p in sorted(ctx.rglob("*")) if p.is_file()
    }
    service.install("devin", scope="project", root=projeto, yes=True)
    depois = {
        p.relative_to(ctx).as_posix(): p.read_bytes() for p in sorted(ctx.rglob("*")) if p.is_file()
    }
    assert snap == depois


def test_uninstall_desregistra_so_o_proprio_forge(projeto):
    from apiforge import _forgecontext as fctx

    service.install("devin", scope="project", root=projeto, yes=True)
    estrangeiro = fctx.build_manifest(
        forge_id="forge-alheia",
        name="Forge Alheia",
        version="1.0.0",
        cli="forge-alheia",
        package="forge_alheia",
        distribution="forge-alheia",
        python_spec=">=3.10",
        scope="project",
        domains=("dominio-alheio",),
        skills=("skill-alheia",),
    )
    fctx.register_forge(projeto, estrangeiro, owner="forge-alheia")

    un = service.uninstall(scope="project", root=projeto, purge=True)
    assert un["status"] == "completed"

    ctx = projeto / ".forge" / "context"
    registry = json.loads((ctx / "registry.json").read_text(encoding="utf-8"))
    assert {e["forge_id"] for e in registry["forges"]} == {"forge-alheia"}
    assert not (ctx / "capabilities" / "api-forge.json").exists()
    assert (ctx / "capabilities" / "forge-alheia.json").exists()


# --------------------------------------------------------------------------
# consumer docs — install-2.0 ciclo 3 (lf-0036)
# --------------------------------------------------------------------------


def test_install_escreve_consumer_docs(projeto):
    out = service.install("devin", scope="project", root=projeto, yes=True)
    assert out["status"] == "completed"
    check = next(c for c in out["checks"] if c["id"] == "consumer-docs")
    assert check["status"] == "PASS"

    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    claude = (projeto / "CLAUDE.md").read_text(encoding="utf-8")
    proto = (projeto / "AGENT_PROTOCOL.md").read_text(encoding="utf-8")
    assert "<!-- forge:ecosystem:begin -->" in agents
    assert "<!-- forge:api-forge:begin -->" in agents
    assert "@AGENTS.md" in claude
    for sec in (
        "1. Discovery",
        "2. Classification",
        "3. Routing",
        "4. Context Retrieval",
        "5. Planning",
        "6. Execution",
        "7. Evaluation",
        "8. Verification",
        "9. Reporting",
    ):
        assert sec in proto
    assert proto.startswith("<!-- forge:agent-protocol:v1 -->")


def test_referencias_protocolo_resolvem(projeto):
    """Refs a AGENT_PROTOCOL.md em assets instalados devem resolver (lf-0034
    achou 113 refs mortas). O doc consumer existe na raiz do workspace."""
    service.install("devin", scope="project", root=projeto, yes=True)
    assert (projeto / "AGENT_PROTOCOL.md").is_file()
    refs = [
        p
        for p in projeto.rglob("*.md")
        if p.is_file()
        and "AGENT_PROTOCOL.md" in p.read_text(encoding="utf-8")
        and ".forge" not in p.parts
    ]
    # refs dentro de mirrors instalados resolvem para a raiz do workspace
    for p in refs:
        assert (projeto / "AGENT_PROTOCOL.md").exists(), p


def test_install_docs_preserva_conteudo_do_usuario(projeto):
    (projeto / "AGENTS.md").write_text("# Minhas regras\n\nTexto do usuario.\n", encoding="utf-8")
    service.install("devin", scope="project", root=projeto, yes=True)
    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    assert agents.startswith("# Minhas regras\n\nTexto do usuario.\n")
    assert "forge:api-forge:begin" in agents


def test_install_docs_idempotente_byte_a_byte(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    nomes = ("AGENTS.md", "CLAUDE.md", "AGENT_PROTOCOL.md")
    snap = {n: (projeto / n).read_bytes() for n in nomes}
    service.install("devin", scope="project", root=projeto, yes=True)
    assert {n: (projeto / n).read_bytes() for n in nomes} == snap


def test_dois_forges_e_uninstall_seletivo(projeto):
    from apiforge import _forgecontext as fctx

    service.install("devin", scope="project", root=projeto, yes=True)
    alheio = fctx.build_manifest(
        forge_id="forge-alheia",
        name="Forge Alheia",
        version="1.0.0",
        cli="forge-alheia",
        package="forge_alheia",
        distribution="forge-alheia",
        python_spec=">=3.10",
        scope="project",
        domains=("dominio-alheio",),
        skills=("skill-alheia",),
    )
    fctx.register_forge(projeto, alheio, owner="forge-alheia")
    fctx.install_docs(projeto, alheio, owner="forge-alheia")

    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    assert agents.count("forge:ecosystem:begin") == 1
    assert "forge:api-forge:begin" in agents
    assert "forge:forge-alheia:begin" in agents

    service.uninstall(scope="project", root=projeto, purge=True)
    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    assert "forge:api-forge" not in agents
    assert "forge:forge-alheia:begin" in agents
    proto = (projeto / "AGENT_PROTOCOL.md").read_text(encoding="utf-8")
    assert "forge:forge-alheia" in proto and "api-forge" not in proto


def test_install_recusa_marcador_ambiguo(projeto):
    (projeto / "AGENTS.md").write_text(
        "# x\n<!-- forge:api-forge:begin -->\na\n"
        "<!-- forge:api-forge:begin -->\nb\n<!-- forge:api-forge:end -->\n",
        encoding="utf-8",
    )
    out = service.install("devin", scope="project", root=projeto, yes=True)
    check = next((c for c in out["checks"] if c["id"] == "context-registry"), None)
    assert check is not None and check["status"] == "BLOCKED"
    assert "FORGE-CONTEXT-CONFLICT" in check["detail"]


def test_install_converge_marker_legado(projeto):
    (projeto / "AGENTS.md").write_text(
        "# minhas regras\n\n<!-- api-forge:managed:begin -->\nold\n"
        "<!-- api-forge:managed:end -->\n",
        encoding="utf-8",
    )
    service.install("devin", scope="project", root=projeto, yes=True)
    agents = (projeto / "AGENTS.md").read_text(encoding="utf-8")
    assert "managed:begin" not in agents
    assert "forge:api-forge:begin" in agents
    assert agents.startswith("# minhas regras\n")


def test_repair_reconstroi_doc_bloco(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    alvo = projeto / "AGENTS.md"
    alvo.write_text(
        alvo.read_text(encoding="utf-8").replace("API Forge", "ADULTERADO"), encoding="utf-8"
    )
    rep = service.repair(scope="project", root=projeto)
    check = next((c for c in rep["checks"] if c["id"] == "consumer-docs"), None)
    assert check is not None and check["status"] == "PASS"
    assert "ADULTERADO" not in alvo.read_text(encoding="utf-8")


def test_uninstall_receipt_persistido_igual_ao_emitido(projeto, monkeypatch):
    """kit.uninstall grava o receipt antes do unregister do contexto — a
    mutacao (BLOCKED -> failed) precisa chegar ao disco."""
    from apiforge import _forgecontext as fctx

    service.install("devin", scope="project", root=projeto, yes=True)

    def boom(*_a, **_k):
        raise fctx.ContextError(fctx.E_CONFLICT, "simulated unregister failure")

    monkeypatch.setattr(fctx, "uninstall_transaction", boom)
    out = service.uninstall(scope="project", root=projeto)
    assert out["status"] == "failed"
    assert any(c["id"] == "context-registry" and c["status"] == "BLOCKED" for c in out["checks"])
    receipts = sorted((projeto / ".apiforge" / "install" / "receipts").glob("uninstall-*.json"))
    assert receipts, "receipt deveria ter sido persistido"
    persisted = json.loads(receipts[-1].read_text("utf-8"))
    assert persisted["status"] == out["status"]
    assert [c["id"] for c in persisted["checks"]] == [c["id"] for c in out["checks"]]


# --------------------------------------------------------------------------
# install-2.1 (cycle-16 wave-04)
# --------------------------------------------------------------------------


def test_workspace_root_explicito_vence_marker(tmp_path):
    """installkit 1.0.6: `--root` e autoritativo no scope workspace — um
    marker de workspace num ancestral nunca desvia o alvo para cima."""
    ws = tmp_path / "ws"
    member = ws / "member"
    member.mkdir(parents=True)
    (ws / "forge.workspace.yaml").write_text("members: []\n", encoding="utf-8")

    out = service.install("devin", scope="workspace", root=member, yes=True)
    assert out["status"] == "completed"
    assert out["target_root"] == str(member.resolve())
    assert (member / ".apiforge" / "install").is_dir()
    assert not (ws / ".apiforge").exists()


def test_workspace_install_escreve_workspace_doc(tmp_path):
    """`forge/WorkspaceInstall/v1` registra o root servido + o receipt."""
    ws = tmp_path / "ws"
    ws.mkdir()
    out = service.install("devin", scope="workspace", root=ws, yes=True)
    doc = json.loads((ws / ".apiforge" / "install" / "workspace-install.json").read_text())
    assert doc["schema"] == "forge/WorkspaceInstall/v1"
    assert doc["workspace_root"] == str(ws.resolve())
    assert doc["projects"][0]["forge_id"] == "api-forge"
    assert doc["projects"][0]["receipt_id"] == out["receipt_id"]


def test_discover_projects_membros_gitless(tmp_path):
    """installkit 1.0.6: `.git` nao e requisito — manifesto de projeto
    (`pyproject.toml`, `package.json`, `forge.json`) torna o diretorio
    membro; diretorio vazio e ignorado."""
    ws = tmp_path / "ws"
    ws.mkdir()
    gitless = ws / "gitless-member"
    gitless.mkdir()
    (gitless / "pyproject.toml").write_text("[project]\nname = 'x'\n")
    deep = ws / "group" / "deep-member"
    deep.mkdir(parents=True)
    (deep / "package.json").write_text("{}")
    (ws / "plain").mkdir()

    found = {p.name for p in kit.discover_projects(ws)}
    assert "gitless-member" in found
    assert "deep-member" in found  # ate max_depth=2, sem .git
    assert "plain" not in found


def test_install_ponteiros_knowledge_namespacados(projeto):
    """Os stubs de knowledge resolvem em `knowledge/api-forge/<rel>` —
    nunca na raiz compartilhada `knowledge/<rel>` (install-2.1)."""
    out = service.install("devin", scope="project", root=projeto, yes=True)
    paths = {f["path"] for f in out["managed_files"]}
    knowledge = [p for p in paths if p.startswith("knowledge/")]
    assert knowledge, "esperava ponteiros de knowledge emitidos"
    assert all(p.startswith("knowledge/api-forge/") for p in knowledge), knowledge

    indice = projeto / "knowledge" / "api-forge" / "README.md"
    assert indice.is_file()
    stub = projeto / "knowledge" / "api-forge" / "neptune" / "README.md"
    assert stub.is_file()
    texto = stub.read_text(encoding="utf-8")
    assert "apiforge knowledge get neptune" in texto
    assert not (projeto / "knowledge" / "neptune").exists()


def _stub_legado(projeto: Path, rel: str, conteudo: bytes, *, disco: bytes | None = None):
    """Grava um stub `knowledge/<rel>` pre-2.1: entrada managed no ledger
    cujo sha registra `conteudo` (disco pode divergir — stub editado)."""
    alvo = projeto / rel
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_bytes(conteudo if disco is None else disco)
    state = projeto / ".apiforge" / "install"
    ledger = kit.Ledger.load(state)
    ledger.record(rel, conteudo, "knowledge", "created")
    ledger.save()
    return alvo


def test_install_migra_stub_legado_intacto(projeto):
    """Stub bare nosso e intacto sai do disco e do ledger — o ponteiro
    namespacado o substitui."""
    service.install("devin", scope="project", root=projeto, yes=True)
    alvo = _stub_legado(projeto, "knowledge/doc-legado.md", b"stub antigo")

    out = service.install("devin", scope="project", root=projeto, yes=True)
    assert not alvo.exists()
    state = projeto / ".apiforge" / "install"
    assert kit.Ledger.load(state).get("knowledge/doc-legado.md") is None
    check = next(c for c in out["checks"] if c["id"] == "knowledge-namespace")
    assert check["status"] == "PASS" and "migrated" in check["detail"]
    migrado = next(f for f in out["managed_files"] if f["path"] == "knowledge/doc-legado.md")
    assert migrado["action"] == "removed"


def test_install_preserva_stub_legado_editado(projeto):
    """Stub bare editado pelo usuario NUNCA e apagado: posse liberada no
    ledger, arquivo fica, recusa nomeada no recibo."""
    service.install("devin", scope="project", root=projeto, yes=True)
    alvo = _stub_legado(
        projeto, "knowledge/doc-editado.md", b"stub original", disco=b"edicao do usuario"
    )

    out = service.install("devin", scope="project", root=projeto, yes=True)
    assert alvo.read_bytes() == b"edicao do usuario"
    state = projeto / ".apiforge" / "install"
    assert kit.Ledger.load(state).get("knowledge/doc-editado.md") is None
    preservado = next(f for f in out["managed_files"] if f["path"] == "knowledge/doc-editado.md")
    assert preservado["action"] == "unchanged"
    assert "preserved" in preservado["note"]


def test_install_nao_toca_knowledge_de_outra_forja(projeto):
    """Arquivo `knowledge/<rel>` sem entrada managed no ledger — de outra
    forja ou do usuario — nao e tocado nem entra no recibo da migracao."""
    service.install("devin", scope="project", root=projeto, yes=True)
    alheio = projeto / "knowledge" / "de-outra-forja.md"
    alheio.write_bytes(b"conteudo alheio")

    out = service.install("devin", scope="project", root=projeto, yes=True)
    assert alheio.read_bytes() == b"conteudo alheio"
    assert not any(f["path"] == "knowledge/de-outra-forja.md" for f in out["managed_files"])


def test_gateway_profile_grava_surface_no_mcp(projeto):
    """`--gateway-profile economy` (e `balanced`) gravam `--surface compact`
    no argv de `.mcp.json` — a flag nao e mais inerte."""
    service.install("devin", scope="project", root=projeto, yes=True, gateway_profile="economy")
    mcp = json.loads((projeto / ".mcp.json").read_text(encoding="utf-8"))
    assert mcp["mcpServers"]["apiforge"] == {
        "command": "apiforge-mcp",
        "args": ["--surface", "compact"],
    }
    comps = json.loads(
        (projeto / ".apiforge" / "install" / "components.json").read_text(encoding="utf-8")
    )
    assert comps["execution_profile"] == "economy"


def test_gateway_profile_deep_surface_full(projeto):
    service.install("devin", scope="project", root=projeto, yes=True, gateway_profile="deep")
    mcp = json.loads((projeto / ".mcp.json").read_text(encoding="utf-8"))
    assert mcp["mcpServers"]["apiforge"]["args"] == ["--surface", "full"]


def test_gateway_profile_invalido_recusa(projeto):
    with pytest.raises(kit.InstallError) as exc:
        service.install("devin", scope="project", root=projeto, yes=True, gateway_profile="turbo")
    assert exc.value.kind == kit.E_PROFILE


def test_repair_reproduz_surface_gravada(projeto):
    """O caminho de leitura usa o `execution_profile` persistido em
    `components.json`: repair restaura o MESMO argv gravado, nao o bare."""
    service.install("devin", scope="project", root=projeto, yes=True, gateway_profile="economy")
    (projeto / ".mcp.json").unlink()
    rep = service.repair(scope="project", root=projeto)
    assert ".mcp.json" in rep["repaired"]
    mcp = json.loads((projeto / ".mcp.json").read_text(encoding="utf-8"))
    assert mcp["mcpServers"]["apiforge"]["args"] == ["--surface", "compact"]


def test_register_propaga_campos_declarados(projeto):
    """`~/.forge/installations/api-forge.json` carrega as declaracoes do
    `forge.json` — verbatim, nunca fabricadas; `depends_on: []` e
    declaracao explicita e fica presente."""
    service.install("devin", scope="project", root=projeto, yes=True)
    manifest = json.loads(
        (Path.home() / ".forge" / "installations" / "api-forge.json").read_text(encoding="utf-8")
    )
    assert manifest["installation_kind"] == "content"
    assert manifest["depends_on"] == []
    install = manifest["install"]
    for flag in ("--gateway-profile", "--components", "--root", "--scope"):
        assert flag in install["flags"]
    assert manifest["mcp"]["verify_tool"] == "portable_status"


def test_profile_components_matriz_declarada():
    """A matriz e dado honesto: minimal = core+mcp; recommended == full
    hoje (full e o slot para defaults mais pesados)."""
    assert set(service.PROFILE_COMPONENTS) == {"minimal", "recommended", "full"}
    assert service.PROFILE_COMPONENTS["minimal"] == ("config", "mcp", "marker", "state")
    assert service.PROFILE_COMPONENTS["recommended"] == service.PROFILE_COMPONENTS["full"]
    for profile, kinds in service.PROFILE_COMPONENTS.items():
        assert tuple(kinds) == kit.profile_asset_kinds(profile)


def test_profile_minimal_sem_assets_opcionais(projeto):
    """`--profile minimal` instala so os kinds declarados na matriz —
    nenhum skill/agent/knowledge."""
    out = service.install("devin", scope="project", root=projeto, profile="minimal", yes=True)
    paths = {f["path"] for f in out["managed_files"]}
    assert not any(p.startswith(("knowledge/", ".agents/", ".claude/")) for p in paths)
    assert (projeto / ".mcp.json").exists()


def test_components_filtra_por_kind(projeto):
    """`--components` sobrescreve por kind: `skills,knowledge` instala os
    mirrors e os ponteiros namespacados, sem agents e sem stubs de
    rules/evals (refs emitidas mas filtradas por kind)."""
    out = service.install(
        "devin",
        scope="project",
        root=projeto,
        yes=True,
        components=("skills", "knowledge"),
    )
    paths = {f["path"] for f in out["managed_files"]}
    assert any(p.startswith(".agents/skills/") for p in paths)
    assert any(p.startswith("knowledge/api-forge/") for p in paths)
    assert not any(p.startswith(".agents/agents/") for p in paths)
    assert not any(p.startswith(("rules/", "evals/")) for p in paths)
