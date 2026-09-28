"""Versioned cache contracts: freshness-aware entries, decisions and delta slices."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract

CacheLayer = Literal[
    "parse",
    "graph",
    "impact",
    "capsule",
    "knowledge",
    "routing",
    "validation",
    "model_response",
]
CACHE_LAYERS: tuple[str, ...] = (
    "parse",
    "graph",
    "impact",
    "capsule",
    "knowledge",
    "routing",
    "validation",
    "model_response",
)
FreshnessState = Literal[
    "miss", "fresh", "stale_harmless", "stale_critical", "invalidated", "corrupt"
]
CacheAction = Literal["reuse", "reuse_warn", "recompute", "invalidate"]
CacheTier = Literal["local", "shared"]
FileStatus = Literal["A", "M", "D", "R", "C", "T", "U", "X"]


class CacheDep(VersionedContract):
    """One source an entry was computed from; a changed sha invalidates the entry.

    Whole file by default; ``span`` narrows it to inclusive lines and
    ``pointers`` to JSON-pointer subtrees of a YAML/JSON document, so an edit
    outside the evidence actually used keeps the entry fresh.
    """

    path: str = Field(min_length=1)
    sha256: str | None = None
    span: tuple[int, int] | None = None
    pointers: tuple[str, ...] = ()


class CacheEntry(VersionedContract):
    """Freshness metadata for one cached payload stored in the content-addressed store."""

    schema: Literal["apiforge/cache-entry/v1"] = "apiforge/cache-entry/v1"  # type: ignore[assignment]
    layer: CacheLayer
    key: str = Field(pattern=r"^[0-9a-f]{64}$")
    subject: str = ""
    object_uri: str = Field(pattern=r"^ctx://sha256/[0-9a-f]{64}$")
    size_bytes: int = Field(default=0, ge=0)
    inputs_sha: str = ""
    policy_sha: str = ""
    expertise_sha: str | None = None
    created_at: str
    expires_at: str | None = None
    deps_files: tuple[CacheDep, ...] = ()

    @field_validator("created_at", "expires_at", mode="after")
    @classmethod
    def iso_timestamp(cls, value: str | None) -> str | None:
        """Tampered or corrupt timestamps make the entry invalid (a corrupt miss)."""
        if value is not None:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        return value

    deps_nodes: tuple[str, ...] = ()
    neighborhood_sha: str | None = None
    symbols: tuple[str, ...] = ()
    manifest_uri: str | None = None


class CacheDecision(VersionedContract):
    """What the store decided for one lookup and why; never hides a reuse."""

    schema: Literal["apiforge/cache-decision/v1"] = "apiforge/cache-decision/v1"  # type: ignore[assignment]
    layer: CacheLayer
    key: str
    subject: str = ""
    state: FreshnessState
    action: CacheAction
    tier: CacheTier | None = None
    reason: str = ""
    warnings: tuple[str, ...] = ()


class ChangedFile(VersionedContract):
    path: str = Field(min_length=1)
    status: FileStatus = "M"


class DeltaSlice(VersionedContract):
    """Delta-first context: what changed, what it impacts, which capsules to build."""

    schema: Literal["apiforge/delta-slice/v1"] = "apiforge/delta-slice/v1"  # type: ignore[assignment]
    source: Literal["git", "explicit"]
    base: str | None = None
    head: str | None = None
    changed_files: tuple[ChangedFile, ...] = ()
    changed_nodes: tuple[str, ...] = ()
    impacted_operations: tuple[str, ...] = ()
    capsule_targets: tuple[str, ...] = ()
    invalidated: tuple[CacheDecision, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved"] = "ready"


__all__ = [
    "CACHE_LAYERS",
    "CacheAction",
    "CacheDecision",
    "CacheDep",
    "CacheEntry",
    "CacheLayer",
    "CacheTier",
    "ChangedFile",
    "DeltaSlice",
    "FreshnessState",
]
