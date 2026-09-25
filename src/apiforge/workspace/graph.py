"""Deterministic virtual graph over independent repositories."""

from __future__ import annotations

import hashlib
from pathlib import Path

from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.workspace import WorkspaceGraph, WorkspaceManifest, WorkspaceRelation


def _node_id(kind: str, value: str) -> str:
    return f"{kind}:{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}"


def build_graph(manifest: WorkspaceManifest) -> WorkspaceGraph:
    nodes: list[dict[str, object]] = [
        {
            "id": _node_id("workspace", manifest.workspace_id),
            "kind": "workspace",
            "name": manifest.name,
            "root": manifest.root,
            "evidence_level": "declared",
        }
    ]
    edges: list[WorkspaceRelation] = []
    workspace_id = nodes[0]["id"]
    for repository in sorted(manifest.repositories, key=lambda item: item.repository_id):
        repository_node = _node_id("repository", repository.repository_id)
        nodes.append(
            {
                "id": repository_node,
                "kind": "repository",
                "name": repository.name,
                "root": repository.root,
                "repository_type": repository.repository_type,
                "exists": Path(repository.root).is_dir(),
                "evidence_level": repository.evidence_level,
            }
        )
        edges.append(
            WorkspaceRelation(
                relation="contains",
                source="workspace.yaml",
                from_id=str(workspace_id),
                to_id=repository_node,
                evidence=EvidenceRecord(
                    level="declared", source="workspace.yaml", refs=(repository.root,)
                ),
                limitations=("repository membership is declared, not runtime deployment proof",),
            )
        )
        if not Path(repository.root).is_dir():
            edges.append(
                WorkspaceRelation(
                    relation="depends_on",
                    source="workspace.yaml",
                    from_id=repository_node,
                    to_id=repository_node,
                    evidence=EvidenceRecord(
                        level="unknown", source="filesystem", refs=(repository.root,)
                    ),
                    limitations=("repository root is missing",),
                )
            )
    edges.extend(manifest.relations)
    unresolved = tuple(
        sorted(
            f"repository {item.name} root is missing: {item.root}"
            for item in manifest.repositories
            if not Path(item.root).is_dir()
        )
    )
    return WorkspaceGraph(
        workspace_id=manifest.workspace_id,
        nodes=tuple(sorted(nodes, key=lambda item: str(item["id"]))),
        edges=tuple(sorted(edges, key=lambda item: (item.from_id, item.to_id, item.relation))),
        unresolved=unresolved,
        evidence_level="declared" if not unresolved else "unknown",
    )


def classify_relation(relation: WorkspaceRelation) -> str:
    return relation.evidence.level


__all__ = ["build_graph", "classify_relation"]
