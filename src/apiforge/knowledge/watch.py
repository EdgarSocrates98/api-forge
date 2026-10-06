"""Freshness Watch (§96): which packs need a refresh, without fetching anything.

The upstream manifest is produced by a separate refresh workflow (§95) and is
only read here: ``{"sources": {<upstream>: {"fingerprint", "version",
"observed_at"}}}``. A pack is compared on its declared fingerprint
(``freshness.source_hash``), ``source_version``, ``expires_at`` and
``window_days`` (measured from the pack's ``verified`` date). Only a stale
pack is reported ``refresh_needed``; a pack without metadata is ``unknown``
and a pack without a manifest entry is ``unresolved``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_resume import FreshnessWatch, PackWatchEntry
from apiforge.knowledge.loader import Pack, load_packs
from apiforge.knowledge.selector import default_root


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def load_manifest(path: Path) -> tuple[dict[str, dict[str, Any]], str]:
    path = Path(path)
    if not path.is_file():
        raise _refusal(
            "AF-KNOW-WATCH-MANIFEST",
            f"upstream manifest {path} does not exist",
            "manifest",
            "record upstream fingerprints with the refresh workflow and pass --manifest",
        )
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise _refusal(
            "AF-KNOW-WATCH-MANIFEST",
            f"upstream manifest {path} is not JSON: {exc}",
            "manifest",
            "write the manifest as UTF-8 JSON",
        ) from exc
    sources = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(sources, dict) or not all(
        isinstance(value, dict) for value in sources.values()
    ):
        raise _refusal(
            "AF-KNOW-WATCH-MANIFEST",
            f"upstream manifest {path} has no 'sources' mapping of objects",
            "manifest",
            'use {"sources": {"<upstream>": {"fingerprint": ..., "version": ...}}}',
        )
    return sources, hashlib.sha256(raw).hexdigest()


def _entry(pack: Pack, sources: dict[str, dict[str, Any]], now: datetime) -> PackWatchEntry:
    metadata = pack.freshness
    if metadata is None:
        return PackWatchEntry(
            pack_id=pack.domain,
            domain=pack.domain,
            state="unknown",
            reasons=("pack declares no freshness metadata",),
            next_action="declare freshness.upstream, source_hash, source_version or expires_at",
        )
    upstream = metadata.upstream or pack.domain
    stale: list[str] = []
    problems: list[str] = []
    if metadata.expires_at:
        try:
            if now > _parse(metadata.expires_at):
                stale.append(f"pack expired at {metadata.expires_at}")
        except ValueError:
            problems.append(f"invalid expires_at {metadata.expires_at!r}")
    if metadata.window_days is not None and pack.verified:
        try:
            age = (now - _parse(pack.verified)).days
            if age > metadata.window_days:
                stale.append(f"pack verified {age}d ago exceeds window {metadata.window_days}d")
        except ValueError:
            problems.append(f"invalid verified date {pack.verified!r}")
    source = sources.get(upstream)
    fingerprint = str(source["fingerprint"]) if source and source.get("fingerprint") else None
    version = str(source["version"]) if source and source.get("version") is not None else None
    if source is None:
        problems.append(f"no upstream manifest entry for {upstream!r}")
    else:
        if metadata.source_hash and fingerprint and fingerprint != metadata.source_hash:
            stale.append("upstream fingerprint differs from the pack declaration")
        if metadata.source_version and version and version != metadata.source_version:
            stale.append(
                f"upstream version {version} differs from declared {metadata.source_version}"
            )
        if not (metadata.source_hash and fingerprint) and not (metadata.source_version and version):
            problems.append("no comparable fingerprint or version between pack and manifest")
    if stale:
        state, action = "refresh_needed", "run the knowledge refresh workflow for this pack"
    elif problems:
        state, action = "unresolved", "record the upstream fingerprint or fix the pack metadata"
    else:
        state, action = "fresh", "none"
    return PackWatchEntry(
        pack_id=pack.domain,
        domain=pack.domain,
        state=state,  # type: ignore[arg-type]
        upstream=upstream,
        declared_fingerprint=metadata.source_hash,
        upstream_fingerprint=fingerprint,
        declared_version=metadata.source_version,
        upstream_version=version,
        reasons=tuple(stale + problems),
        next_action=action,
    )


def watch_packs(manifest: Path, *, now: str, root: Path | None = None) -> FreshnessWatch:
    """Compare every pack with the upstream manifest; never fetches, never rewrites a pack."""
    try:
        clock = _parse(now)
    except ValueError as exc:
        raise _refusal(
            "AF-KNOW-WATCH-CLOCK", f"invalid --now {now!r}: {exc}", "now", "pass an ISO8601 clock"
        ) from exc
    sources, digest = load_manifest(manifest)
    packs = load_packs(default_root(root))
    entries = tuple(_entry(packs[name], sources, clock) for name in sorted(packs))
    return FreshnessWatch(
        now=now,
        manifest_sha256=digest,
        entries=entries,
        refresh_needed=tuple(item.pack_id for item in entries if item.state == "refresh_needed"),
    )


__all__ = ["load_manifest", "watch_packs"]
