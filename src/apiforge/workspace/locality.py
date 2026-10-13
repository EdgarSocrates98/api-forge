"""Workspace locality-first (§48–49): target repo, direct neighbors, transitive only on request.

A workspace is never "all repositories concatenated". The plan starts at the
target, adds repositories that share a declared relation with it
(`depends_on`, `client_of`, `calls`, `deploys`), and lists the next hop as
deferred unless the caller asks for it — evidence must justify going further.
"""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_extras import LocalityPlan, LocalityTier

_RELATIONS = {"depends_on", "client_of", "calls", "deploys"}


def plan_locality(root: Path, target: str, *, transitive: bool = False) -> LocalityPlan:
    from apiforge.workspace.discovery import discover
    from apiforge.workspace.manifests import load_workspace_manifest

    base = Path(root).resolve()
    direct_file = base / "workspace.yaml"
    manifest_path = direct_file if direct_file.is_file() else discover(base).workspace_manifest
    if not manifest_path:
        error = ContractError("AF-ROOT-NOT-FOUND", f"no workspace manifest discovered from {root}")
        error.field = "root"  # type: ignore[attr-defined]
        error.unlock = "run `apiforge workspace init` or point --root at a workspace"  # type: ignore[attr-defined]
        raise error
    manifest = load_workspace_manifest(manifest_path)
    by_id = {repo.repository_id: repo.name for repo in manifest.repositories}
    by_name = {repo.name: repo.repository_id for repo in manifest.repositories}
    target_id = by_name.get(target) or (target if target in by_id else None)
    if target_id is None:
        error = ContractError(
            "AF-WORKSPACE-TARGET-UNKNOWN", f"{target!r} is not a workspace repository"
        )
        error.field = "target"  # type: ignore[attr-defined]
        error.unlock = f"use one of {sorted(by_name)}"  # type: ignore[attr-defined]
        raise error
    neighbors: dict[str, set[str]] = {repo_id: set() for repo_id in by_id}
    for relation in manifest.relations:
        if relation.relation not in _RELATIONS:
            continue
        if relation.from_id in neighbors and relation.to_id in neighbors:
            neighbors[relation.from_id].add(relation.to_id)
            neighbors[relation.to_id].add(relation.from_id)
    direct = sorted(neighbors[target_id] - {target_id})
    second = sorted({item for repo in direct for item in neighbors[repo]} - {target_id, *direct})
    tiers = (
        LocalityTier(
            tier="target", repositories=(by_id[target_id],), reason="the repository being changed"
        ),
        LocalityTier(
            tier="direct",
            repositories=tuple(by_id[item] for item in direct),
            reason="declared relation with the target",
        ),
        LocalityTier(
            tier="transitive",
            repositories=tuple(by_id[item] for item in second),
            included=transitive,
            reason="included on request"
            if transitive
            else "deferred: needs evidence (--transitive)",
        ),
    )
    reached = {target_id, *direct, *(second if transitive else [])}
    return LocalityPlan(
        target=by_id[target_id],
        tiers=tiers,
        excluded=tuple(sorted(by_id[item] for item in by_id if item not in reached)),
    )


__all__ = ["plan_locality"]
