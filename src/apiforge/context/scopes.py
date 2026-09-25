"""Closed scope and target vocabulary."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextScope


def validate_scope(scope: str, *, root: Path, target: str | None = None, impact: str | None = None) -> ContextScope:
    if scope not in {"repo", "workspace", "target"}:
        raise ContractError(
            "AF-CONTEXT-SCOPE-INVALID",
            f"scope {scope!r} is not one of repo, workspace, target",
        )
    if scope == "target" and not target:
        raise ContractError("AF-CONTEXT-SCOPE-INVALID", "target scope requires --target")
    if impact and impact not in {"direct", "transitive", "all"}:
        raise ContractError("AF-CONTEXT-SCOPE-INVALID", f"impact {impact!r} is unsupported")
    return ContextScope(scope=scope, root=str(Path(root).resolve()), target=target, impact=impact)  # type: ignore[arg-type]


def scope_roots(scope: ContextScope, *, project_root: Path | None, workspace_root: Path | None) -> tuple[Path, ...]:
    if scope.scope == "repo":
        return (Path(project_root or scope.root).resolve(),)
    if scope.scope == "workspace":
        return (Path(workspace_root or scope.root).resolve(),)
    return (Path(scope.root).resolve(),)


__all__ = ["scope_roots", "validate_scope"]
