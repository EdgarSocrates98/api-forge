import json
import subprocess
from pathlib import Path

import pytest

from apiforge.sandbox.worktree import (
    WorktreeError,
    worktree_create,
    worktree_list,
    worktree_remove,
)


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "t@t.dev")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / ".gitignore").write_text(".apiforge/\n", encoding="utf-8")
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "init")
    return tmp_path


def test_create_refuses_non_git(tmp_path: Path) -> None:
    with pytest.raises(WorktreeError, match="AF-WORKTREE-NO-GIT"):
        worktree_create(tmp_path, "feat-x")


def test_name_must_match_pattern(repo: Path) -> None:
    with pytest.raises(WorktreeError, match="AF-WORKTREE-NAME-INVALID"):
        worktree_create(repo, "Bad_Name")


def test_create_registers_index(repo: Path) -> None:
    result = worktree_create(repo, "feat-x")
    wt = repo / ".apiforge" / "worktrees" / "feat-x"
    assert wt.is_dir()
    assert result["branch"] == "apiforge/feat-x"
    index = json.loads(
        (repo / ".apiforge" / "worktrees" / "index.json").read_text(encoding="utf-8")
    )
    assert index["worktrees"]["feat-x"]["branch"] == "apiforge/feat-x"


def test_existing_worktree_refused(repo: Path) -> None:
    worktree_create(repo, "feat-x")
    with pytest.raises(WorktreeError, match="AF-WORKTREE-EXISTS"):
        worktree_create(repo, "feat-x")


def test_dirty_repo_refused(repo: Path) -> None:
    (repo / "f.txt").write_text("dirty", encoding="utf-8")
    with pytest.raises(WorktreeError, match="AF-WORKTREE-DIRTY"):
        worktree_create(repo, "feat-x")
    result = worktree_create(repo, "feat-x", force=True)
    assert result["forced"] is True


def test_list_reports_drift(repo: Path) -> None:
    worktree_create(repo, "feat-x")
    listed = worktree_list(repo)
    assert listed["drift"] == []
    _git(repo, "worktree", "remove", ".apiforge/worktrees/feat-x", "--force")
    listed = worktree_list(repo)
    assert any("feat-x" in d for d in listed["drift"])


def test_remove_cleans_index(repo: Path) -> None:
    worktree_create(repo, "feat-x")
    worktree_remove(repo, "feat-x")
    assert not (repo / ".apiforge" / "worktrees" / "feat-x").exists()
    assert worktree_list(repo)["worktrees"] == {}
