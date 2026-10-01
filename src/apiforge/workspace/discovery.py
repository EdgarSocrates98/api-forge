"""Bounded, read-only ancestor discovery for projects and workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Discovery:
    start: Path
    module_root: Path
    repository_root: Path | None
    project_manifest: Path | None
    workspace_manifest: Path | None
    evidence: tuple[str, ...]

    @property
    def project_root(self) -> Path | None:
        return (
            self.project_manifest.parent.parent if self.project_manifest else self.repository_root
        )

    @property
    def workspace_root(self) -> Path | None:
        return self.workspace_manifest.parent.parent if self.workspace_manifest else None


def ancestors(start: Path) -> tuple[Path, ...]:
    current = Path(start).resolve()
    values: list[Path] = []
    while True:
        values.append(current)
        if current.parent == current:
            return tuple(values)
        current = current.parent


def find_repo_root(start: Path) -> Path | None:
    for candidate in ancestors(start):
        if (candidate / ".git").exists():
            return candidate
    return None


def find_project_manifest(start: Path) -> Path | None:
    for candidate in ancestors(start):
        path = candidate / ".apiforge" / "project.yaml"
        if path.is_file():
            return path
    return None


def find_workspace_manifest(start: Path, *, stop: Path | None = None) -> Path | None:
    boundary = stop.resolve() if stop else None
    for candidate in ancestors(start):
        path = candidate / ".apiforge" / "workspace.yaml"
        if path.is_file():
            return path
        if boundary and candidate == boundary:
            break
    return None


def discover(
    start: Path | None = None,
    *,
    project_root: Path | None = None,
    workspace_root: Path | None = None,
    discover_parent: bool = True,
) -> Discovery:
    module = Path(start or Path.cwd()).resolve()
    repository = project_root.resolve() if project_root else find_repo_root(module)
    project = (
        project_root.resolve() / ".apiforge" / "project.yaml"
        if project_root and (project_root / ".apiforge" / "project.yaml").is_file()
        else find_project_manifest(module)
    )
    base = workspace_root.resolve() if workspace_root else (repository or module)
    workspace = (
        base / ".apiforge" / "workspace.yaml"
        if workspace_root and (base / ".apiforge" / "workspace.yaml").is_file()
        else find_workspace_manifest(
            base if discover_parent else module, stop=base if workspace_root else None
        )
    )
    evidence = [f"module:{module}"]
    evidence.append(f"repository:{repository}" if repository else "repository:unresolved")
    evidence.append(f"project:{project}" if project else "project:unresolved")
    evidence.append(f"workspace:{workspace}" if workspace else "workspace:unresolved")
    return Discovery(module, module, repository, project, workspace, tuple(evidence))


__all__ = [
    "Discovery",
    "ancestors",
    "discover",
    "find_project_manifest",
    "find_repo_root",
    "find_workspace_manifest",
]
