"""Freshness decisions (§25): dependency probes first, TTL second, never a silent reuse."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from apiforge.cache.policy import LayerPolicy
from apiforge.contracts.cache import CacheAction, CacheDep, CacheEntry, FreshnessState


class Probe(Protocol):
    """Current-state oracle used to decide whether an entry still describes reality."""

    def dep_sha(self, dep: CacheDep) -> str | None: ...

    def neighborhood_sha(self, nodes: tuple[str, ...]) -> str | None: ...

    def symbol_changed(self, manifest_uri: str, symbols: tuple[str, ...]) -> str | None: ...


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def iso(moment: datetime) -> str:
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)


def assess(
    entry: CacheEntry,
    policy: LayerPolicy,
    *,
    now: datetime,
    probe: Probe | None = None,
) -> tuple[FreshnessState, CacheAction, str]:
    """Return (state, action, reason) for one entry against the current state."""
    if probe is not None:
        exclude = getattr(probe, "exclude", None)
        if exclude is not None:
            exclude(dep.path for dep in entry.deps_files)
        for dep in entry.deps_files:
            current = probe.dep_sha(dep)
            if current != dep.sha256:
                change = "removed" if current is None else "changed"
                where = f":{dep.span[0]}-{dep.span[1]}" if dep.span else ""
                where += f"#{','.join(dep.pointers)}" if dep.pointers else ""
                return "invalidated", "invalidate", f"dependency {dep.path}{where} {change}"
        if entry.neighborhood_sha is not None:
            current_neighborhood = probe.neighborhood_sha(entry.deps_nodes)
            if current_neighborhood != entry.neighborhood_sha:
                return "invalidated", "invalidate", "graph neighborhood of dependency nodes changed"
        if entry.manifest_uri and entry.symbols:
            hit = probe.symbol_changed(entry.manifest_uri, entry.symbols)
            if hit is not None:
                return "invalidated", "invalidate", hit
    if entry.expires_at is not None and parse_iso(entry.expires_at) <= now:
        if policy.on_stale == "warn":
            return "stale_harmless", "reuse_warn", f"expired at {entry.expires_at}; reuse allowed"
        return "stale_critical", "recompute", f"expired at {entry.expires_at}; policy recompute"
    return "fresh", "reuse", "dependencies unchanged and within ttl"


__all__ = ["Probe", "assess", "iso", "now_utc", "parse_iso"]
