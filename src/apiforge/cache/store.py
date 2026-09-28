"""Advisory layered cache: local tier under the root, optional shared tier by env/flag.

Entries live at ``<tier>/entries/<layer>/<key>.json``; payloads at
``<tier>/objects/<sha256>`` named by the content hash and re-verified on every
read. Any read failure is a ``corrupt`` miss — the caller recomputes; the cache
never turns a recoverable condition into an error.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from apiforge.cache.freshness import Probe, assess, iso, now_utc, parse_iso
from apiforge.cache.policy import LayerPolicy, load_policies, policy_for, policy_sha
from apiforge.contracts.cache import (
    CACHE_LAYERS,
    CacheDecision,
    CacheDep,
    CacheEntry,
    CacheTier,
)

ENV_HOME = "APIFORGE_CACHE_HOME"
_CTX_PREFIX = "ctx://sha256/"


def normalize(text: str) -> str:
    """Same LF normalization as the ctx gateway, kept local to avoid an import cycle."""
    return text.replace(chr(13) + chr(10), chr(10)).replace(chr(13), chr(10))


def uri_for(text: str) -> str:
    return _CTX_PREFIX + hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


ENV_SWITCH = "APIFORGE_CACHE"


def cache_enabled(flag: bool | None = None) -> bool:
    if flag is not None:
        return flag
    return os.environ.get(ENV_SWITCH, "on").strip().lower() not in {"off", "0", "false", "no"}


@dataclass(frozen=True)
class _Tier:
    name: CacheTier
    dir: Path

    def entry_path(self, layer: str, key: str) -> Path:
        return self.dir / "entries" / layer / f"{key}.json"

    def object_path(self, uri: str) -> Path:
        return self.dir / "objects" / uri.rsplit("/", 1)[-1]

    def read_object(self, uri: str) -> str | None:
        path = self.object_path(uri)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return None
        return text if uri_for(text) == uri else None

    def write_object(self, text: str) -> str:
        uri = uri_for(text)
        path = self.object_path(uri)
        if not path.is_file():
            _atomic_write(path, normalize(text))
        return uri


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


class CacheStore:
    """Local tier always; shared tier only when a cache home is configured."""

    def __init__(
        self,
        root: Path,
        *,
        home: Path | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.enabled = cache_enabled(enabled)
        shared_home = home or (Path(os.environ[ENV_HOME]) if os.environ.get(ENV_HOME) else None)
        self.local = _Tier("local", self.root / ".apiforge" / "cache")
        self.shared = _Tier("shared", Path(shared_home).resolve()) if shared_home else None

    # ------------------------------------------------------------------ reads
    def lookup(
        self,
        layer: str,
        key: str,
        *,
        probe: Probe | None = None,
        now: datetime | None = None,
    ) -> tuple[CacheDecision, str | None]:
        policy = policy_for(layer)
        if not self.enabled:
            return _decision(layer, key, "miss", "recompute", reason="cache disabled"), None
        moment = now or now_utc()
        corrupt: CacheDecision | None = None
        for tier in self._tiers(policy):
            path = tier.entry_path(layer, key)
            if not path.is_file():
                continue
            entry = _read_entry(path)
            payload = tier.read_object(entry.object_uri) if entry is not None else None
            if entry is None or payload is None:
                corrupt = _decision(
                    layer,
                    key,
                    "corrupt",
                    "recompute",
                    tier=tier.name,
                    reason=f"unreadable {path.name}",
                )
                continue
            state, action, reason = assess(entry, policy, now=moment, probe=probe)
            decision = _decision(
                layer,
                key,
                state,
                action,
                tier=tier.name,
                subject=entry.subject,
                reason=reason,
                warnings=(reason,) if action == "reuse_warn" else (),
            )
            if action in {"reuse", "reuse_warn"}:
                if tier.name == "shared":
                    self.local.write_object(payload)
                    _atomic_write(self.local.entry_path(layer, key), _dump_entry(entry))
                return decision, payload
            if action == "invalidate":
                _unlink(path)
            return decision, None
        return corrupt or _decision(layer, key, "miss", "recompute", reason="no entry"), None

    def read_object(self, uri: str) -> str | None:
        for tier in (self.local, self.shared):
            if tier is not None:
                text = tier.read_object(uri)
                if text is not None:
                    return text
        return None

    # ----------------------------------------------------------------- writes
    def put(
        self,
        layer: str,
        key: str,
        payload: str,
        *,
        subject: str = "",
        inputs_sha: str = "",
        deps_files: Iterable[CacheDep] = (),
        deps_nodes: Iterable[str] = (),
        neighborhood_sha: str | None = None,
        symbols: Iterable[str] = (),
        manifest: str | None = None,
        now: datetime | None = None,
    ) -> CacheEntry | None:
        policy = policy_for(layer)
        if not self.enabled:
            return None
        moment = now or now_utc()
        tiers = self._tiers(policy)
        object_uri = ""
        manifest_uri: str | None = None
        for tier in tiers:
            object_uri = tier.write_object(payload)
            if manifest is not None:
                manifest_uri = tier.write_object(manifest)
        entry = CacheEntry(
            layer=layer,  # type: ignore[arg-type]
            key=key,
            subject=subject,
            object_uri=object_uri,
            size_bytes=len(normalize(payload).encode("utf-8")),
            inputs_sha=inputs_sha,
            policy_sha=policy_sha(),
            created_at=iso(moment),
            expires_at=iso(moment + timedelta(seconds=policy.ttl_seconds))
            if policy.ttl_seconds
            else None,
            deps_files=tuple(
                sorted(deps_files, key=lambda dep: (dep.path, dep.span or (0, 0), dep.pointers))
            ),
            deps_nodes=tuple(sorted(set(deps_nodes))),
            neighborhood_sha=neighborhood_sha,
            symbols=tuple(sorted(set(symbols))),
            manifest_uri=manifest_uri,
        )
        text = _dump_entry(entry)
        for tier in tiers:
            try:
                _atomic_write(tier.entry_path(layer, key), text)
            except OSError:
                continue
        return entry

    def invalidate(
        self,
        *,
        files: Iterable[str] = (),
        nodes: Iterable[str] = (),
        layers: Iterable[str] = CACHE_LAYERS,
    ) -> list[CacheDecision]:
        """Drop entries whose dependency files or nodes intersect the change set."""
        changed_files = {Path(item).as_posix() for item in files}
        changed_nodes = set(nodes)
        dropped: list[CacheDecision] = []
        for tier, path, entry in self.entries(layers):
            if entry is None:
                continue
            hit_files = sorted(changed_files & {dep.path for dep in entry.deps_files})
            hit_nodes = sorted(changed_nodes & set(entry.deps_nodes))
            if not hit_files and not hit_nodes:
                continue
            _unlink(path)
            dropped.append(
                _decision(
                    entry.layer,
                    entry.key,
                    "invalidated",
                    "invalidate",
                    tier=tier.name,
                    subject=entry.subject,
                    reason="depends on " + ", ".join([*hit_files, *hit_nodes]),
                )
            )
        return sorted(dropped, key=lambda item: (item.layer, item.subject, item.key))

    # ------------------------------------------------------------ inspection
    def entries(
        self, layers: Iterable[str] = CACHE_LAYERS
    ) -> Iterator[tuple[_Tier, Path, CacheEntry | None]]:
        wanted = tuple(layers)
        for tier in (self.local, self.shared):
            if tier is None:
                continue
            for layer in wanted:
                folder = tier.dir / "entries" / layer
                if not folder.is_dir():
                    continue
                for path in sorted(folder.glob("*.json")):
                    yield tier, path, _read_entry(path)

    def stats(self, *, now: datetime | None = None) -> dict[str, Any]:
        moment = now or now_utc()
        policies = load_policies()
        layers: dict[str, dict[str, Any]] = {}
        for tier, _, entry in self.entries():
            layer = entry.layer if entry is not None else "unknown"
            row = layers.setdefault(
                layer, {"entries": 0, "bytes": 0, "expired": 0, "corrupt": 0, "tiers": {}}
            )
            row["tiers"][tier.name] = row["tiers"].get(tier.name, 0) + 1
            if entry is None:
                row["corrupt"] += 1
                continue
            row["entries"] += 1
            row["bytes"] += entry.size_bytes
            if entry.expires_at and parse_iso(entry.expires_at) <= moment:
                row["expired"] += 1
        graph_dir = self.root / ".apiforge" / "ctx" / "graph"
        graphs = sorted(p.name for p in graph_dir.iterdir()) if graph_dir.is_dir() else []
        return {
            "schema": "apiforge/cache-stats/v1",
            "enabled": self.enabled,
            "tiers": {
                "local": str(self.local.dir),
                "shared": str(self.shared.dir) if self.shared else None,
            },
            "layers": {name: layers[name] for name in sorted(layers)},
            "graph_snapshots": len(graphs),
            "policies": {
                name: {
                    "enabled": policy.enabled,
                    "ttl_seconds": policy.ttl_seconds,
                    "on_stale": policy.on_stale,
                    "shared": policy.shared,
                }
                for name, policy in policies.items()
            },
        }

    def gc(self, *, apply: bool = False, now: datetime | None = None) -> dict[str, Any]:
        """Report (or delete with ``apply``) expired/corrupt entries and orphan objects."""
        moment = now or now_utc()
        remove_entries: list[Path] = []
        live: dict[str, set[str]] = {"local": set(), "shared": set()}
        for tier, path, entry in self.entries():
            expired = (
                entry is not None
                and entry.expires_at is not None
                and parse_iso(entry.expires_at) <= moment
            )
            if entry is None or expired:
                remove_entries.append(path)
                continue
            live[tier.name].add(entry.object_uri.rsplit("/", 1)[-1])
            if entry.manifest_uri:
                live[tier.name].add(entry.manifest_uri.rsplit("/", 1)[-1])
        remove_objects: list[Path] = []
        for maybe in (self.local, self.shared):
            if maybe is None:
                continue
            folder = maybe.dir / "objects"
            if folder.is_dir():
                remove_objects.extend(
                    path for path in sorted(folder.iterdir()) if path.name not in live[maybe.name]
                )
        ctx_orphans = self._ctx_orphans()
        if apply:
            for path in [*remove_entries, *remove_objects, *ctx_orphans]:
                _unlink(path)
        return {
            "schema": "apiforge/cache-gc/v1",
            "applied": apply,
            "entries": [self._display(path) for path in remove_entries],
            "objects": len(remove_objects),
            "ctx_orphans": len(ctx_orphans),
            "bytes": sum(_size(path) for path in [*remove_entries, *remove_objects, *ctx_orphans]),
        }

    # -------------------------------------------------------------- helpers
    def _tiers(self, policy: LayerPolicy) -> list[_Tier]:
        tiers = [self.local]
        if self.shared is not None and policy.shared:
            tiers.append(self.shared)
        return tiers

    def _ctx_orphans(self) -> list[Path]:
        """ctx objects referenced by no ledger row and no live capsule selection."""
        ctx_dir = self.root / ".apiforge" / "ctx"
        if not ctx_dir.is_dir():
            return []
        referenced: set[str] = set()
        ledger = self.root / ".apiforge" / "economy.jsonl"
        if ledger.is_file():
            for line in ledger.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for ref in row.get("refs") or []:
                    if isinstance(ref, dict) and isinstance(ref.get("uri"), str):
                        referenced.add(ref["uri"].rsplit("/", 1)[-1])
        for tier, _, entry in self.entries(("capsule",)):
            if entry is None:
                continue
            payload = tier.read_object(entry.object_uri)
            if payload is None:
                continue
            try:
                body = json.loads(payload)
            except json.JSONDecodeError:
                continue
            for candidate in body.get("candidates") or []:
                referenced.add(uri_for(str(candidate.get("content", ""))).rsplit("/", 1)[-1])
        return [
            path
            for path in sorted(ctx_dir.iterdir())
            if path.is_file() and len(path.name) == 64 and path.name not in referenced
        ]

    def _display(self, path: Path) -> str:
        for base in (self.root, self.shared.dir if self.shared else None):
            if base is None:
                continue
            try:
                return path.relative_to(base).as_posix()
            except ValueError:
                continue
        return path.as_posix()


def _decision(
    layer: str,
    key: str,
    state: str,
    action: str,
    *,
    tier: CacheTier | None = None,
    subject: str = "",
    reason: str = "",
    warnings: tuple[str, ...] = (),
) -> CacheDecision:
    return CacheDecision(
        layer=layer,  # type: ignore[arg-type]
        key=key,
        subject=subject,
        state=state,  # type: ignore[arg-type]
        action=action,  # type: ignore[arg-type]
        tier=tier,
        reason=reason,
        warnings=warnings,
    )


def _read_entry(path: Path) -> CacheEntry | None:
    try:
        return CacheEntry.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValidationError):
        return None


def _dump_entry(entry: CacheEntry) -> str:
    return json.dumps(entry.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"


def _unlink(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass


def _size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


__all__ = ["ENV_HOME", "ENV_SWITCH", "CacheStore", "cache_enabled"]
