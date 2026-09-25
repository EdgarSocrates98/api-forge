"""Resolve scope, targets and impact inputs from bounded local evidence."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from apiforge.context.scopes import validate_scope
from apiforge.contracts.context import ContextScope, ContextTarget
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord
from apiforge.contracts.workspace import WorkspaceStatus
from apiforge.workspace.discovery import Discovery, discover


def resolve_scope(
    root: Path | None = None,
    *,
    scope: str = "repo",
    target: str | None = None,
    impact: str | None = None,
) -> tuple[ContextScope, Discovery]:
    start = Path(root or Path.cwd()).resolve()
    found = discover(start)
    project_root = found.project_root or found.repository_root or start
    workspace_root = found.workspace_root
    resolved_root = workspace_root if scope == "workspace" and workspace_root else project_root
    context_scope = validate_scope(scope, root=resolved_root, target=target, impact=impact)
    return context_scope, found


def resolve_targets(scope: ContextScope, status: WorkspaceStatus | None) -> tuple[ContextTarget, ...]:
    if status is None or status.graph is None:
        return ()
    targets: list[ContextTarget] = []
    for node in status.graph.nodes:
        node_id = str(node.get("id", ""))
        kind = str(node.get("kind", "unknown"))
        root = str(node.get("root", status.workspace.root if status.workspace else scope.root))
        if kind == "workspace" or kind == "repository":
            targets.append(
                ContextTarget(
                    target_id=node_id,
                    label=str(node.get("name", node_id)),
                    kind=kind,
                    root=root,
                    evidence=EvidenceRecord(
                        level=cast(EvidenceLevel, str(node.get("evidence_level", "unknown"))),
                        source="workspace-graph",
                        refs=(root,),
                    ),
                )
            )
    return tuple(sorted(targets, key=lambda item: item.target_id))


__all__ = ["resolve_scope", "resolve_targets"]
