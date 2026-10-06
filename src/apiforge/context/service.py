"""Canonical context service combining graph scope and measured funnel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.application.funnel import measure_funnel
from apiforge.context.resolver import resolve_scope, resolve_targets
from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextResult
from apiforge.contracts.evidence import EvidenceRecord
from apiforge.workspace.service import WorkspaceService


class ContextService:
    """Compose context without executing consumer code or external providers."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root or Path.cwd()).resolve()

    def resolve(
        self,
        *,
        scope: str = "repo",
        target: str | None = None,
        impact: str | None = None,
    ) -> ContextResult:
        context_scope, discovery = resolve_scope(
            self.root, scope=scope, target=target, impact=impact
        )
        workspace_status = WorkspaceService(self.root).status()
        targets = resolve_targets(context_scope, workspace_status)
        if target:
            selected = tuple(
                item for item in targets if target in {item.target_id, item.label, item.root}
            )
            if not selected:
                raise ContractError(
                    "AF-CONTEXT-TARGET-NOT-FOUND",
                    f"target {target!r} was not discovered in the selected scope",
                )
            targets = selected
        included = tuple(sorted({item.root for item in targets}))
        if not included:
            included = (str(context_scope.root),)
        graph_payload = (
            workspace_status.graph.model_dump(mode="json") if workspace_status.graph else {}
        )
        funnel_path = Path(context_scope.root) / ".apiforge" / "case"
        funnel: dict[str, Any] = (
            measure_funnel(funnel_path)
            if funnel_path.is_dir()
            else {
                "case_dir": str(funnel_path),
                "stages": [],
                "reduction": {},
                "diagnostics": [
                    {"code": "AF-FUNNEL-ARTIFACT-MISSING", "detail": "case is not initialized"}
                ],
            }
        )
        diagnostics = funnel.get("diagnostics", ())
        funnel_gaps = tuple(
            str(item.get("detail", ""))
            for item in diagnostics
            if isinstance(item, dict) and item.get("detail")
        )
        gaps = tuple(sorted(set(workspace_status.gaps + funnel_gaps)))
        return ContextResult(
            scope=context_scope,
            targets=targets,
            included_repositories=included,
            facts=tuple(
                {"kind": "discovery", "path": item, "evidence_level": "observed"}
                for item in discovery.evidence
            ),
            graph=graph_payload,
            funnel=funnel,
            evidence=(
                EvidenceRecord(
                    level="observed", source="bounded-discovery", refs=discovery.evidence
                ),
            ),
            gaps=gaps,
            unresolved=gaps,
            status="ready" if not gaps else "degraded",
            evidence_level="observed" if not gaps else "unknown",
        )


__all__ = ["ContextService"]
