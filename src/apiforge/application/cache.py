"""Cache and delta application facade shared by CLI and MCP."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from apiforge.cache.errors import CacheError


def cache_stats(root: Path | None = None, *, cache_home: Path | None = None) -> dict[str, Any]:
    from apiforge.cache.store import CacheStore

    return CacheStore(Path(root or Path.cwd()), home=cache_home).stats()


def cache_invalidate(
    root: Path | None = None,
    *,
    changed: Sequence[str] = (),
    base: str | None = None,
    head: str | None = None,
    case_dir: Path | None = None,
    cache_home: Path | None = None,
) -> dict[str, Any]:
    delta = context_delta(
        root,
        changed=changed,
        base=base,
        head=head,
        case_dir=case_dir,
        invalidate=True,
        cache_home=cache_home,
    )
    return {
        "schema": "apiforge/cache-invalidation/v1",
        "changed_files": [item["path"] for item in delta.get("changed_files", [])],
        "invalidated": delta.get("invalidated", []),
        "kept_targets": sorted(set(_capsule_subjects(Path(root or Path.cwd()), cache_home))),
        "unresolved": delta.get("unresolved", []),
    }


def context_delta(
    root: Path | None = None,
    *,
    changed: Sequence[str] = (),
    base: str | None = None,
    head: str | None = None,
    case_dir: Path | None = None,
    invalidate: bool = False,
    cache_home: Path | None = None,
) -> dict[str, Any]:
    from apiforge.context.delta import build_delta

    delta = build_delta(
        Path(root or Path.cwd()),
        base=base,
        head=head,
        changed=changed,
        case_dir=case_dir,
        invalidate=invalidate,
        cache_home=cache_home,
    )
    return delta.model_dump(mode="json")


def context_gc(
    root: Path | None = None, *, apply: bool = False, cache_home: Path | None = None
) -> dict[str, Any]:
    from apiforge.cache.store import CacheStore

    return CacheStore(Path(root or Path.cwd()), home=cache_home).gc(apply=apply)


def cache_lookup_layer(layer: str) -> dict[str, Any]:
    """Refuse unknown/disabled layers with the cataloged codes (used by `cache stats --layer`)."""
    from apiforge.cache.policy import policy_for

    policy = policy_for(layer)
    return {"layer": policy.layer, "enabled": policy.enabled, "ttl_seconds": policy.ttl_seconds}


def _capsule_subjects(root: Path, cache_home: Path | None) -> list[str]:
    from apiforge.cache.store import CacheStore

    return [
        entry.subject
        for _, _, entry in CacheStore(root, home=cache_home).entries(("capsule",))
        if entry is not None and entry.subject
    ]


__all__ = [
    "CacheError",
    "cache_invalidate",
    "cache_lookup_layer",
    "cache_stats",
    "context_delta",
    "context_gc",
]
