"""Git worktree isolation. Argument arrays only; never shell=True."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

_NAME_RE = re.compile(r"^[a-z0-9-]+$")


class WorktreeError(RuntimeError):
    def __init__(self, code: str, detail: str, field: str | None = None) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.field = field


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise WorktreeError(
            "AF-WORKTREE-GIT-FAILED",
            result.stderr.strip() or f"git {' '.join(args)} exited {result.returncode}",
        )
    return result.stdout


def _require_repo(root: Path) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise WorktreeError(
            "AF-WORKTREE-NO-GIT",
            f"{root} is not inside a git work tree",
            field="root",
        )


def _index_dir(root: Path) -> Path:
    return Path(root) / ".apiforge" / "worktrees"


def _load_index(root: Path) -> dict[str, Any]:
    index_file = _index_dir(root) / "index.json"
    if not index_file.is_file():
        return {"worktrees": {}}
    data = json.loads(index_file.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"worktrees": {}}


def _save_index(root: Path, index: dict[str, Any]) -> None:
    d = _index_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.json").write_text(json.dumps(index, indent=2, sort_keys=True), encoding="utf-8")


def _is_dirty(root: Path) -> bool:
    out = _git(root, "status", "--porcelain")
    return any(
        not line[3:].lstrip().startswith(".apiforge/") for line in out.splitlines() if line.strip()
    )


def _git_worktree_paths(root: Path) -> set[str]:
    out = _git(root, "worktree", "list", "--porcelain")
    return {line.split(" ", 1)[1] for line in out.splitlines() if line.startswith("worktree ")}


def worktree_create(root: Path, name: str, force: bool = False) -> dict[str, Any]:
    root = Path(root).resolve()
    _require_repo(root)
    if not _NAME_RE.match(name):
        raise WorktreeError(
            "AF-WORKTREE-NAME-INVALID",
            f"{name!r} must match ^[a-z0-9-]+$",
            field="name",
        )
    index = _load_index(root)
    path = _index_dir(root) / name
    if name in index["worktrees"] or path.exists():
        raise WorktreeError(
            "AF-WORKTREE-EXISTS",
            f"worktree {name!r} already registered or present on disk",
            field="name",
        )
    if _is_dirty(root) and not force:
        raise WorktreeError(
            "AF-WORKTREE-DIRTY",
            "repository has uncommitted changes; pass force to record the override",
            field="root",
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    branch = f"apiforge/{name}"
    _git(root, "worktree", "add", str(path), "-b", branch)
    index["worktrees"][name] = {
        "path": str(path),
        "branch": branch,
        "forced": force,
    }
    _save_index(root, index)
    return {"name": name, "path": str(path), "branch": branch, "forced": force}


def worktree_list(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    _require_repo(root)
    index = _load_index(root)
    actual = _git_worktree_paths(root)
    drift: list[str] = []
    for name, entry in index["worktrees"].items():
        if str(Path(entry["path"]).resolve()) not in {str(Path(p).resolve()) for p in actual}:
            drift.append(f"{name}: indexed but absent from git worktree list")
    base = str(_index_dir(root).resolve())
    for p in actual:
        if str(Path(p).resolve()).startswith(base) and Path(p).name not in index["worktrees"]:
            drift.append(f"{Path(p).name}: on disk but not indexed")
    return {"worktrees": index["worktrees"], "drift": sorted(drift)}


def worktree_remove(root: Path, name: str) -> dict[str, Any]:
    root = Path(root).resolve()
    _require_repo(root)
    index = _load_index(root)
    entry = index["worktrees"].get(name)
    if entry is None:
        raise WorktreeError(
            "AF-WORKTREE-UNKNOWN",
            f"no worktree named {name!r} in the index",
            field="name",
        )
    _git(root, "worktree", "remove", entry["path"], "--force")
    _git(root, "branch", "-D", entry["branch"])
    del index["worktrees"][name]
    _save_index(root, index)
    return {"removed": name}
