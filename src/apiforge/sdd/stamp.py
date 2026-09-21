"""``sdd stamp``: write only the upstream hash line of an artifact.

The stamp performs frontmatter line surgery — the ``upstream:`` block is
replaced (or inserted before the closing fence) while every other byte,
including line endings, is preserved.
"""

from __future__ import annotations

import os
from pathlib import Path

from apiforge.core.io import text_sha256
from apiforge.core.yaml import StrictLoadError, load_yaml_mapping
from apiforge.sdd.models import SddError, StampResult

_BOM = "﻿"


def _fences(lines: list[str]) -> tuple[int, int] | None:
    """Return (open, close) fence line indexes, or None."""
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return 0, index
    return None


def stamp(path: Path, upstream: Path) -> StampResult:
    """Rewrite ``upstream:`` in ``path``'s frontmatter to point at ``upstream``."""
    path = Path(path)
    upstream = Path(upstream)
    if not upstream.is_file():
        raise SddError("AF-SDD-STAMP", f"upstream file does not exist: {upstream}")
    text = path.read_text(encoding="utf-8")
    eol = "\r\n" if "\r\n" in text else "\n"
    bom = text.startswith(_BOM)
    lines = text.lstrip(_BOM).split(eol)
    fences = _fences(lines)
    if fences is None:
        raise SddError("AF-SDD-STAMP", f"{path.name}: no frontmatter block")
    open_i, close_i = fences

    block_text = eol.join(lines[open_i + 1 : close_i]) + eol
    previous: str | None = None
    try:
        meta = load_yaml_mapping(block_text, source=path.name)
        raw_upstream = meta.get("upstream")
        if isinstance(raw_upstream, dict) and isinstance(raw_upstream.get("sha256"), str):
            previous = raw_upstream["sha256"]
    except StrictLoadError:
        pass

    digest = text_sha256(upstream)
    relative = Path(os.path.relpath(upstream, path.parent)).as_posix()
    block = [
        "upstream:",
        f"  path: {relative}",
        f'  sha256: "{digest}"',
    ]

    # Locate an existing top-level `upstream:` key inside the frontmatter and
    # replace it plus its indented children; otherwise insert before the fence.
    start = end = None
    for index in range(open_i + 1, close_i):
        line = lines[index]
        if line.startswith(("upstream:", "upstream :")):
            start = index
            end = index + 1
            while end < close_i and (lines[end].startswith((" ", "\t")) or not lines[end]):
                end += 1
            break
    if start is None:
        lines[close_i:close_i] = block
    else:
        lines[start:end] = block

    new_text = eol.join(lines)
    if bom:
        new_text = _BOM + new_text
    changed = new_text != text
    if changed:
        path.write_text(new_text, encoding="utf-8", newline="")
    return StampResult(
        path=str(path),
        upstream=relative,
        sha256=digest,
        previous=previous,
        changed=changed,
    )
