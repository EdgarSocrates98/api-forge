"""Canonical context and impact application facade."""

from __future__ import annotations

from pathlib import Path

from apiforge.context.service import ContextService


def resolve_context(
    root: Path | None = None,
    *,
    scope: str = "repo",
    target: str | None = None,
    impact: str | None = None,
) -> object:
    return ContextService(root).resolve(scope=scope, target=target, impact=impact)


__all__ = ["resolve_context"]
