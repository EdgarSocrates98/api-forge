"""detail_level projection: representation, never content.

`summary` drops verbose text fields (rationale, remediation, measures,
bodies) but never refuses codes, fact_ids or verdict fields. `normal` and
`full` are today identical — `full` gains raw payloads only when producers
start emitting them.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LEVELS = ("summary", "normal", "full")

_DROP_KEYS = frozenset(
    {
        "rationale",
        "remediation",
        "snippet",
        "body",
        "measures",
        "attrs",
        "proves",
        "next_steps",
    }
)


def _project(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _project(item) for key, item in value.items() if key not in _DROP_KEYS}
    if isinstance(value, (list, tuple)):
        return [_project(item) for item in value]
    return value


def apply_detail_level(payload: Any, level: str) -> Any:
    """Project ``payload`` at ``level``; content-bearing fields never mutate."""
    if level not in LEVELS:
        raise ValueError(f"AF-DETAIL-LEVEL: unknown level {level!r}")
    if level == "summary":
        return _project(payload)
    return payload
