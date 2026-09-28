"""Application-facing workspace composition."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from apiforge.contracts.base import ContractError
from apiforge.contracts.workspace import (
    RepositoryRef,
    WorkspaceGraph,
    WorkspaceManifest,
    WorkspaceStatus,
)
from apiforge.workspace.discovery import Discovery, discover
from apiforge.workspace.graph import build_graph
from apiforge.workspace.manifests import (
    add_repository,
    init_workspace_manifest,
    load_project_manifest,
    load_workspace_manifest,
    write_workspace_manifest,
)


class WorkspaceService:
    """Resolve and inspect workspace state without executing repository code."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root or Path.cwd()).resolve()

    def discovery(self, *, workspace_root: Path | None = None) -> Discovery:
        return discover(self.root, workspace_root=workspace_root)

    def status(self, *, workspace_root: Path | None = None) -> WorkspaceStatus:
        found = self.discovery(workspace_root=workspace_root)
        gaps: list[str] = []
        project = load_project_manifest(found.project_manifest) if found.project_manifest else None
        workspace = (
            load_workspace_manifest(found.workspace_manifest) if found.workspace_manifest else None
        )
        if project is None:
            gaps.append("AF-ROOT-NOT-FOUND: project manifest was not discovered")
        if workspace is None:
            gaps.append("AF-ROOT-NOT-FOUND: workspace manifest was not discovered")
        graph = build_graph(workspace) if workspace else None
        if graph:
            gaps.extend(graph.unresolved)
        status: Literal["ready", "degraded", "unresolved", "blocked"] = (
            "ready" if not gaps else "degraded"
        )
        if not project and not workspace:
            status = "unresolved"
        return WorkspaceStatus(
            workspace=workspace,
            graph=graph,
            discovered_project=project,
            gaps=tuple(sorted(set(gaps))),
            status=status,
        )

    def init(
        self, *, workspace: bool = False, name: str | None = None
    ) -> WorkspaceManifest | object:
        if workspace:
            return init_workspace_manifest(self.root, name=name)
        from apiforge.workspace.manifests import init_project_manifest

        return init_project_manifest(self.root)

    def add(
        self, repository_root: Path, *, workspace_root: Path | None = None
    ) -> WorkspaceManifest:
        target = (workspace_root or self.root).resolve()
        manifest_path = target / ".apiforge" / "workspace.yaml"
        if manifest_path.is_file():
            manifest = load_workspace_manifest(manifest_path)
        else:
            manifest = init_workspace_manifest(target)
        repo_root = Path(repository_root).resolve()
        if not repo_root.is_dir():
            raise ContractError("AF-WORKSPACE-REPO-MISSING", str(repo_root))
        project_path = repo_root / ".apiforge" / "project.yaml"
        repository_id = hashlib.sha256(str(repo_root).encode("utf-8")).hexdigest()[:16]
        repository = RepositoryRef(
            repository_id=f"repository:{repository_id}",
            name=repo_root.name,
            root=str(repo_root),
            project_manifest=str(project_path) if project_path.is_file() else None,
            evidence_level="observed",
        )
        updated = add_repository(manifest, repository)
        write_workspace_manifest(target, updated)
        return updated

    def graph(
        self,
        *,
        infer: bool = False,
        run_id: str | None = None,
        workspace_root: Path | None = None,
    ) -> WorkspaceGraph:
        found = self.discovery(workspace_root=workspace_root)
        if found.workspace_manifest is None:
            raise ContractError("AF-ROOT-NOT-FOUND", "workspace manifest was not discovered")
        manifest = load_workspace_manifest(found.workspace_manifest)
        if not infer:
            return build_graph(manifest)
        from apiforge.workspace.inference import infer_relations

        result = infer_relations(manifest)
        gaps = list(result.unresolved)
        gaps.extend(self._attribute_inference(run_id, len(result.relations)))
        return build_graph(
            manifest, inferred=result.relations, inferred_unresolved=tuple(sorted(set(gaps)))
        )

    def _attribute_inference(self, run_id: str | None, edges: int) -> list[str]:
        if not run_id:
            return [
                (
                    "AF-WORKSPACE-INFER-UNATTRIBUTED: inference ran without --run-id; "
                    "field records cannot see it"
                )
            ]
        from apiforge.contracts.economy import CostVector, RunLedgerEntry
        from apiforge.economy.run_ledger import PERSIST_FAILURE, append

        entry = RunLedgerEntry(
            run_id=run_id,
            verb="workspace.infer",
            source="graph",
            cost=CostVector(expansions=edges),
        )
        if append(self.root, entry, auditable=True):
            return []
        return [f"{PERSIST_FAILURE}: workspace.infer row for {run_id} was not persisted"]


__all__ = ["WorkspaceService"]
