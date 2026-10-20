"""Ciclo 12 review — `knowledge freshness|drift` sem `--root` nao pode quebrar.

Regressao: o default passou a `None` mas os corpos ainda faziam
`load_pack(root / domain)` — TypeError mascarado como AF-CLI-INPUT. Estes
testes rodam de um cwd sem `knowledge/` para exercitar o resolver empacotado.
"""

from __future__ import annotations

import json

from typer.testing import CliRunner

from apiforge.cli import app


def test_freshness_default_root_resolves(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # sem knowledge/ no cwd → resolver empacotado
    runner = CliRunner()
    result = runner.invoke(app, ["knowledge", "freshness", "api-lifecycle", "--now", "2026-01-01"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["source"] == "api-lifecycle"
    assert "age_days" in payload


def test_drift_default_root_resolves(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["knowledge", "drift", "api-lifecycle", "--now", "2026-01-01"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["domain"] == "api-lifecycle"
    assert "verdict" in payload or "observations" in payload or "conflicts" in payload


def test_explicit_root_still_honored(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    missing = tmp_path / "no-such-knowledge"
    result = runner.invoke(
        app,
        ["knowledge", "freshness", "api-lifecycle", "--now", "2026-01-01", "--root", str(missing)],
    )
    # Recusa AF-* nomeada, nao fallback silencioso para o pacote.
    assert result.exit_code != 0
    assert "AF-" in result.output


def test_mcp_knowledge_show_default_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from apiforge.mcp import tools

    out = tools.knowledge_show("api-lifecycle")
    assert out["domain"] == "api-lifecycle"


def test_mcp_knowledge_check_default_root(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from apiforge.mcp import tools

    out = tools.knowledge_check()
    assert out["ok"] is True


def test_mcp_knowledge_show_explicit_root_missing_refuses(tmp_path, monkeypatch):
    import pytest

    monkeypatch.chdir(tmp_path)
    from apiforge.knowledge.loader import KnowledgeError
    from apiforge.mcp import tools

    # Recusa nomeada (AF-KNOW-*) — nao cai silenciosamente no corpus empacotado.
    with pytest.raises(KnowledgeError, match="AF-KNOW"):
        tools.knowledge_show("api-lifecycle", root=str(tmp_path / "nada"))
