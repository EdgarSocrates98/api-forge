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
    assert any(p.startswith(".devin/skills/") for p in paths)
    assert any(p.startswith(".agents/skills/") for p in paths)
    mcp = json.loads((projeto / ".mcp.json").read_text(encoding="utf-8"))
    assert "apiforge" in mcp["mcpServers"]
    assert "api-forge:managed" in (projeto / "AGENTS.md").read_text("utf-8")
    receipts = list((projeto / ".apiforge" / "install" / "receipts").glob("*.json"))
    assert receipts


def test_install_profile_full_inclui_agents(projeto):
    out = service.install(
        "devin", scope="project", root=projeto, profile="full", yes=True)
    paths = {f["path"] for f in out["managed_files"]}
    assert any(p.startswith(".devin/agents/") for p in paths)
    assert any(p.startswith(".agents/agents/") for p in paths)


def test_install_profile_minimal_sem_mirrors(projeto):
    out = service.install(
        "devin", scope="project", root=projeto, profile="minimal", yes=True)
    assert out["status"] == "completed"
    assert not (projeto / ".devin").exists()
    assert (projeto / ".mcp.json").exists()


def test_install_nao_sobrescreve_arquivo_do_usuario(projeto):
    plano = service.install("devin", scope="project", root=projeto,
                            dry_run=True)
    alvo_rel = next(f["path"] for f in plano["planned_files"]
                    if f["path"].startswith(".devin/skills/")
                    and f["path"].endswith("SKILL.md"))
    alvo = projeto / alvo_rel
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text("conteudo do usuario", encoding="utf-8")
    service.install("devin", scope="project", root=projeto, yes=True)
    assert alvo.read_text(encoding="utf-8") == "conteudo do usuario"


def test_install_dry_run_planeja_sem_escrever(projeto):
    out = service.install("devin", scope="project", root=projeto,
                          dry_run=True)
    assert out["status"] == "planned"
    assert not (projeto / ".devin").exists()
    assert not (projeto / ".mcp.json").exists()


def test_status_e_drift(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    st = service.status(scope="project", root=projeto)
    assert st["status"] == "healthy"
    alvo = projeto / next(
        p["path"] for p in service.status(
            scope="project", root=projeto)["drift"]["modified"]
        or [{"path": ".devin/skills/api-forge-core/SKILL.md"}])
    alvo = projeto / ".devin/skills/api-forge-core/SKILL.md"
    alvo.write_text("edicao manual", encoding="utf-8")
    st2 = service.status(scope="project", root=projeto)
    assert st2["status"] == "degraded"


def test_repair_restaura(projeto):
    service.install("devin", scope="project", root=projeto, yes=True)
    vitima = projeto / ".devin/skills/api-forge-core/SKILL.md"
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
    assert resto == []


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
    assert out["status"] in ("PASS", "FAIL", "BLOCKED", "NOT_APPLICABLE",
                             "UNVERIFIED")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def test_cli_install_dry_run(projeto):
    result = CliRunner().invoke(
        app, ["install", "--host", "devin", "--root", str(projeto),
              "--dry-run"])
    assert result.exit_code == 0, result.stdout
    doc = json.loads(result.stdout)
    assert doc["status"] == "planned"


def test_cli_install_sem_aprovacao_falha_com_recusa(projeto):
    result = CliRunner().invoke(
        app, ["install", "--host", "devin", "--root", str(projeto)])
    assert result.exit_code != 0
    assert "FORGE-INSTALL-PLAN-NOT-APPROVED" in (
        result.stdout + (result.stderr or ""))


def test_cli_install_status(projeto):
    CliRunner().invoke(
        app, ["install", "--host", "devin", "--root", str(projeto), "--yes"])
    result = CliRunner().invoke(
        app, ["install", "status", "--root", str(projeto)])
    assert result.exit_code == 0, result.stdout
    doc = json.loads(result.stdout)
    assert doc["forge_id"] == "api-forge"
    assert doc["status"] == "healthy"


def test_cli_install_uninstall(projeto):
    CliRunner().invoke(
        app, ["install", "--host", "devin", "--root", str(projeto), "--yes"])
    result = CliRunner().invoke(
        app, ["install", "uninstall", "--root", str(projeto), "--purge"])
    assert result.exit_code == 0, result.stdout
    resto = [p for p in _arquivos(projeto) if not p.startswith(".git/")]
    assert resto == []
