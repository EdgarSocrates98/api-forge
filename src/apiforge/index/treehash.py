"""Content digest over a source tree — the cache/index invalidation key."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

SOURCE_EXTS = frozenset({".py", ".java", ".go"})
_IGNORE_DIRS = frozenset(
    {".git", ".apiforge", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache"}
)


def _iter_sources(project: Path) -> Iterator[Path]:
    stack = [project]
    while stack:
        current = stack.pop()
        for entry in sorted(current.iterdir()):
            if entry.is_dir():
                if entry.name not in _IGNORE_DIRS:
                    stack.append(entry)
            elif entry.suffix in SOURCE_EXTS:
                yield entry


def source_entries(project: Path) -> list[dict[str, Any]]:
    """Sorted `{path, sha256, bytes}` rows for every source file."""
    rows: list[dict[str, Any]] = []
    for path in _iter_sources(Path(project)):
        rel = path.relative_to(project).as_posix()
        rows.append(
            {
                "path": rel,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
            }
        )
    rows.sort(key=lambda r: r["path"])
    return rows


def source_digest(project: Path) -> tuple[str, list[dict[str, Any]]]:
    """Digest over sorted `path:sha256` lines — the invalidation key."""
    rows = source_entries(project)
    text = "".join(f"{r['path']}:{r['sha256']}\n" for r in rows)
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), rows
