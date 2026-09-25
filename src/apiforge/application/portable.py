"""Canonical portable distribution application operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.distribution.assets import asset_inventory
from apiforge.distribution.doctor import diagnose
from apiforge.distribution.paths import resolve_paths
from apiforge.workspace.discovery import discover
from apiforge.workspace.manifests import init_project_manifest, init_workspace_manifest


def inspect(root: Path | None = None) -> dict[str, Any]:
    base = Path(root or Path.cwd()).resolve()
    paths = resolve_paths(cwd=base)
    found = discover(base)
    return {
        "status": "ready",
        "paths": paths.contract().model_dump(mode="json"),
        "discovery": {
            "module_root": str(found.module_root),
            "repository_root": str(found.repository_root) if found.repository_root else None,
            "project_manifest": str(found.project_manifest) if found.project_manifest else None,
            "workspace_manifest": str(found.workspace_manifest) if found.workspace_manifest else None,
            "evidence": list(found.evidence),
        },
        "assets": [
            {"name": item.name, "sha256": item.sha256, "path": str(item.path)}
            for item in asset_inventory()
        ],
        "limitations": [
            "host activation is optional and plan-only",
            "network/provider freshness is not inferred from local inspection",
        ],
    }


def initialize(root: Path | None = None, *, workspace: bool = False, name: str | None = None) -> object:
    base = Path(root or Path.cwd()).resolve()
    manifest = init_workspace_manifest(base, name=name) if workspace else init_project_manifest(base)
    return {
        "status": "ready",
        "manifest": str(base / ".apiforge" / ("workspace.yaml" if workspace else "project.yaml")),
        "payload": manifest.model_dump(mode="json"),
        "mutation": "local-minimal-manifest-only",
        "evidence_level": "declared",
    }


def status(root: Path | None = None) -> dict[str, Any]:
    base = Path(root or Path.cwd()).resolve()
    from apiforge.workspace.service import WorkspaceService

    workspace_status = WorkspaceService(base).status()
    return {
        "status": workspace_status.status,
        "paths": resolve_paths(cwd=base).contract().model_dump(mode="json"),
        "project": workspace_status.discovered_project.model_dump(mode="json")
        if workspace_status.discovered_project
        else None,
        "workspace": workspace_status.workspace.model_dump(mode="json") if workspace_status.workspace else None,
        "graph": workspace_status.graph.model_dump(mode="json") if workspace_status.graph else None,
        "gaps": list(workspace_status.gaps),
        "unresolved": list(workspace_status.gaps),
        "evidence_level": "observed" if workspace_status.status == "ready" else "unknown",
    }


def doctor(root: Path | None = None) -> object:
    return diagnose(Path(root or Path.cwd()))


__all__ = ["doctor", "initialize", "inspect", "status"]
