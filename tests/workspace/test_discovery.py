from pathlib import Path

from apiforge.workspace.discovery import discover


def test_discovery_finds_nested_repository_and_project(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    nested = root / "src" / "service"
    (root / ".git").mkdir(parents=True)
    (root / ".apiforge").mkdir()
    (root / ".apiforge" / "project.yaml").write_text(
        "project_id: test\nroot: .\n", encoding="utf-8"
    )
    nested.mkdir(parents=True)
    found = discover(nested)
    assert found.repository_root == root.resolve()
    assert found.project_manifest == root.joinpath(".apiforge", "project.yaml").resolve()
