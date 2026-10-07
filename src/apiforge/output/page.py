"""§42 standardized large-response shape: summary/items/refs/evidence/unresolved/pagination.

``paged`` bounds any item list into a declared window — the caller keeps the
full set upstream (artifacts, refs), the response stays honest about what it
carries: ``total`` always reports the real cardinality, ``next_offset`` is
``null`` when the window reaches the end.
"""

from __future__ import annotations

from typing import Any, cast

from apiforge.contracts.tool_surface import PageWindow, ToolPage


def paged(
    items: list[Any] | tuple[Any, ...],
    *,
    offset: int = 0,
    limit: int = 50,
    summary: str = "",
    refs: tuple[str, ...] = (),
    evidence: tuple[Any, ...] = (),
    unresolved: tuple[str, ...] = (),
) -> ToolPage:
    """Project ``items`` into a bounded ``ToolPage`` window."""
    total = len(items)
    window = tuple(items[offset : offset + limit])
    next_offset = offset + limit if offset + limit < total else None
    return ToolPage(
        summary=summary or f"{total} item(s); showing {len(window)} from offset {offset}",
        items=window,
        refs=refs,
        evidence=evidence,
        unresolved=unresolved,
        pagination=PageWindow(offset=offset, limit=limit, total=total, next_offset=next_offset),
    )


def bound_collections[T](payload: T, limit: int | None) -> T:
    """§42 truncate top-level collection values to ``limit`` items.

    Counts and totals computed upstream stay truthful — the bound only cuts
    the carried window; callers needing the full set page or read artifacts.
    """
    if limit is None or not isinstance(payload, dict):
        return payload
    return cast(
        T,
        {
            key: value[:limit] if isinstance(value, list) else value
            for key, value in payload.items()
        },
    )


__all__ = ["bound_collections", "paged"]
