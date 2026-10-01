"""Extractor cache keyed by content hash — hits are recorded, never hidden.

Key = sha256(CACHE_VERSION | framework | source_digest). A changed file
produces a different key, so stale entries are unreachable garbage, not
wrong answers. A corrupt or schema-invalid cache file is treated as a miss
and rewritten — the extractor is always the source of truth.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from apiforge.adapters.inventory import CodeInventory
from apiforge.index.treehash import source_digest

CACHE_VERSION = "extractor/2"


def _key(project: Path, framework: str) -> str:
    digest, _ = source_digest(project)
    return hashlib.sha256(f"{CACHE_VERSION}|{framework}|{digest}".encode()).hexdigest()


def extract_cached(
    project: Path,
    framework: str,
    extractor: Callable[[Path], Any],
    cache_dir: Path | None,
    ledger_root: Path | None = None,
) -> tuple[Any, dict[str, Any]]:
    """Return (inventory, cache_meta); `cache_meta` names hit/miss + key."""
    if cache_dir is None:
        return extractor(project), {"enabled": False}
    key = _key(project, framework)
    path = Path(cache_dir) / f"{key}.json"
    hit = False
    inventory: Any = None
    if path.is_file():
        try:
            inventory = CodeInventory.model_validate(json.loads(path.read_text(encoding="utf-8")))
            hit = True
        except (json.JSONDecodeError, ValidationError, OSError):
            inventory = None
    if inventory is None:
        inventory = extractor(project)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(inventory.model_dump(mode="json"), sort_keys=True),
                encoding="utf-8",
            )
        except OSError:
            pass
    if ledger_root is not None:
        try:
            from apiforge.economy.ledger import record

            record(
                Path(ledger_root),
                verb=f"cache:extract:{framework}",
                detail_level="hit" if hit else "miss",
                payload_bytes=path.stat().st_size if path.is_file() else 0,
            )
        except OSError:
            pass
    return inventory, {"enabled": True, "hit": hit, "key": key[:16]}
