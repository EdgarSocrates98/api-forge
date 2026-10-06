"""Independent repository discovery and virtual workspace graph services."""

from apiforge.workspace.discovery import Discovery, discover
from apiforge.workspace.graph import build_graph
from apiforge.workspace.manifests import (
    init_project_manifest,
    init_workspace_manifest,
    load_project_manifest,
    load_workspace_manifest,
    write_project_manifest,
    write_workspace_manifest,
)
from apiforge.workspace.service import WorkspaceService

__all__ = [
    "Discovery",
    "WorkspaceService",
    "build_graph",
    "discover",
    "init_project_manifest",
    "init_workspace_manifest",
    "load_project_manifest",
    "load_workspace_manifest",
    "write_project_manifest",
    "write_workspace_manifest",
]
