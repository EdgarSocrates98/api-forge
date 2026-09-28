"""`--output json|compact` (§42): the same payload, cheaper to transport.

``compact`` is lossless by rule: it removes only ``None``, empty strings and
empty containers (recursively) and drops indentation. Every non-empty value
— including ``0`` and ``false`` — survives, so
``json.loads(render(v, "compact")) == prune(v)``.
"""

from __future__ import annotations

import json
import os
from typing import Any

from apiforge.contracts.base import ContractError

MODES = ("json", "compact")
ENV_OUTPUT = "APIFORGE_OUTPUT"
_EMPTY: tuple[Any, ...] = (None, "", [], {})


def prune(value: Any) -> Any:
    if isinstance(value, dict):
        kept = {key: prune(item) for key, item in value.items()}
        return {key: item for key, item in kept.items() if not _empty(item)}
    if isinstance(value, list | tuple):
        return [prune(item) for item in value]
    return value


def _empty(value: Any) -> bool:
    return value is None or (isinstance(value, str | list | dict) and len(value) == 0)


def resolve_mode(flag: str | None = None) -> str:
    mode = (flag or os.environ.get(ENV_OUTPUT) or "json").strip().lower()
    if mode not in MODES:
        error = ContractError("AF-OUTPUT-MODE-INVALID", f"output mode {mode!r} is not json|compact")
        error.field = "output"  # type: ignore[attr-defined]
        error.unlock = "pass --output json or --output compact"  # type: ignore[attr-defined]
        raise error
    return mode


def render(value: Any, mode: str = "json") -> str:
    if mode == "compact":
        return json.dumps(prune(value), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return json.dumps(value, sort_keys=True, ensure_ascii=True, indent=2)


__all__ = ["ENV_OUTPUT", "MODES", "prune", "render", "resolve_mode"]
