from pathlib import Path
from types import SimpleNamespace

import pytest

from apiforge.knowledge import selector
from apiforge.knowledge.retrieval import search
from apiforge.knowledge.selector import knowledge_generation


@pytest.fixture(autouse=True)
def _no_triggers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(selector, "select_expertise", lambda *a, **k: SimpleNamespace(selected=()))


AUTH = """sources:
  - name: fixture
    url: https://example.invalid/spec
    authority: ietf-rfc
    verified: "2026-09-01"
"""


def _pack(root: Path, name: str, body: str) -> Path:
    pack = root / name
    pack.mkdir(parents=True, exist_ok=True)
    (pack / "pack.yaml").write_text(
        f'domain: {name}\nversion: 1\nsummary: fixture\nverified: "2026-09-01"\n', encoding="utf-8"
    )
    (pack / "source_authority.yaml").write_text(AUTH, encoding="utf-8")
    (pack / "patterns.md").write_text(body, encoding="utf-8")
    return pack


def test_portuguese_terms_are_retrieved(tmp_path: Path) -> None:
    _pack(
        tmp_path,
        "seguranca",
        "# Padrões\n\n## Autenticação\n\nUse autenticação mútua e migração segura.\n",
    )
    _pack(tmp_path, "outro", "# Outro\n\n## Paginação\n\nCursor opaco.\n")
    result = search("autenticação", root=tmp_path)
    assert result.passages
    assert result.passages[0].pack_id == "seguranca"
    assert "autenticação" in result.expanded_terms


def test_pack_edited_on_disk_is_seen_without_restart(tmp_path: Path) -> None:
    pack = _pack(tmp_path, "seguranca", "# Padrões\n\n## Tokens\n\nRotacione tokens.\n")
    assert not search("configuração", root=tmp_path).passages
    (pack / "patterns.md").write_text(
        "# Padrões\n\n## Configuração\n\nConfiguração por ambiente, nunca no código.\n",
        encoding="utf-8",
    )
    result = search("configuração", root=tmp_path)
    assert result.passages and result.passages[0].heading == "Configuração"


def test_generation_changes_when_a_pack_file_changes(tmp_path: Path) -> None:
    pack = _pack(tmp_path, "seguranca", "# A\n")
    before = knowledge_generation(tmp_path)
    (pack / "patterns.md").write_text("# A\n\n## B\n\nnew\n", encoding="utf-8")
    assert knowledge_generation(tmp_path) != before
