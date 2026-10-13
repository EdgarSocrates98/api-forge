"""Strict YAML manifest persistence with explicit, minimal write operations."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.workspace import ProjectManifest, RepositoryRef, WorkspaceManifest
from apiforge.core.yaml import StrictLoadError, load_yaml_mapping


def _id(prefix: str, path: Path) -> str:
    return f"{prefix}:{hashlib.sha256(str(path.resolve()).encode('utf-8')).hexdigest()[:16]}"


def _read(path: Path) -> dict[str, Any]:
    try:
        value = load_yaml_mapping(path.read_text(encoding="utf-8"), source=str(path))
    except (OSError, UnicodeDecodeError, StrictLoadError) as exc:
        raise ContractError("AF-MANIFEST-INVALID", f"{path}: {exc}") from exc
    return dict(value)


def load_project_manifest(path: Path) -> ProjectManifest:
    target = Path(path)
    if not target.is_file():
        raise ContractError("AF-MANIFEST-INVALID", f"project manifest missing: {target}")
    data = _read(target)
    data.setdefault("project_id", _id("project", target.parent.parent))
    base = target.parent.parent.resolve()
    data.setdefault("root", str(base))
    root = Path(str(data["root"])).expanduser()
    data["root"] = str((base / root if not root.is_absolute() else root).resolve())
    try:
        return ProjectManifest.model_validate(data)
    except ValueError as exc:
        raise ContractError("AF-MANIFEST-INVALID", f"{target}: {exc}") from exc


def _repository(data: dict[str, Any], workspace_root: Path) -> RepositoryRef:
    root = Path(str(data.get("root", ""))).expanduser()
    if not root.is_absolute():
        root = workspace_root / root
    root = root.resolve()
    item = dict(data)
    item.setdefault("repository_id", _id("repository", root))
    item.setdefault("name", root.name or "repository")
    item["root"] = str(root)
    manifest = root / ".apiforge" / "project.yaml"
    if manifest.is_file():
        item.setdefault("project_manifest", str(manifest))
    return RepositoryRef.model_validate(item)


def load_workspace_manifest(path: Path) -> WorkspaceManifest:
    target = Path(path)
    if not target.is_file():
        raise ContractError("AF-MANIFEST-INVALID", f"workspace manifest missing: {target}")
    data = _read(target)
    root = target.parent.parent.resolve()
    data.setdefault("workspace_id", _id("workspace", root))
    data.setdefault("name", root.name or "workspace")
    data.setdefault("root", str(root))
    raw_repositories = data.get("repositories", [])
    if not isinstance(raw_repositories, list):
        raise ContractError("AF-MANIFEST-INVALID", f"{target}: repositories must be a list")
    data["repositories"] = [_repository(dict(item), root) for item in raw_repositories]
    try:
        return WorkspaceManifest.model_validate(data)
    except ValueError as exc:
        raise ContractError("AF-MANIFEST-INVALID", f"{target}: {exc}") from exc


def _dump(path: Path, value: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=True, allow_unicode=False), encoding="utf-8")
    return path


def init_project_manifest(root: Path, *, hosts: tuple[str, ...] = ()) -> ProjectManifest:
    target = Path(root).resolve()
    manifest = ProjectManifest(project_id=_id("project", target), root=str(target), hosts=hosts)
    write_project_manifest(target, manifest)
    return manifest


def init_workspace_manifest(root: Path, *, name: str | None = None) -> WorkspaceManifest:
    target = Path(root).resolve()
    manifest = WorkspaceManifest(
        workspace_id=_id("workspace", target),
        name=name or target.name or "workspace",
        root=str(target),
    )
    write_workspace_manifest(target, manifest)
    return manifest


def write_project_manifest(root: Path, manifest: ProjectManifest) -> Path:
    target = Path(root).resolve() / ".apiforge" / "project.yaml"
    return _dump(target, manifest.model_dump(mode="json", exclude={"version"}))


def write_workspace_manifest(root: Path, manifest: WorkspaceManifest) -> Path:
    target = Path(root).resolve() / ".apiforge" / "workspace.yaml"
    return _dump(target, manifest.model_dump(mode="json", exclude={"version"}))


def add_repository(manifest: WorkspaceManifest, repository: RepositoryRef) -> WorkspaceManifest:
    if any(item.root == repository.root for item in manifest.repositories):
        return manifest
    return manifest.model_copy(update={"repositories": (*manifest.repositories, repository)})


__all__ = [
    "add_repository",
    "init_project_manifest",
    "init_workspace_manifest",
    "load_project_manifest",
    "load_workspace_manifest",
    "write_project_manifest",
    "write_workspace_manifest",
]
