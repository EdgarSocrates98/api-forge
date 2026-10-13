"""Deterministic redaction and bounded cardinality helpers."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

_SECRET = re.compile(r"(authorization|api[-_]?key|token|password|secret|cookie)", re.IGNORECASE)
_ID = re.compile(r"^[0-9a-f]{8,}$", re.IGNORECASE)


def redact_attributes(
    attributes: Mapping[str, Any], allowed: set[str] | None = None
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in attributes.items():
        if allowed is not None and key not in allowed:
            continue
        result[key] = "[REDACTED]" if _SECRET.search(key) else value
    return result


def normalize_route(route: str | None) -> str | None:
    if route is None:
        return None
    return "/".join(":id" if _ID.fullmatch(part) else part for part in route.split("/"))


def cardinality(attributes: Mapping[str, Any]) -> int:
    return len({str(value) for value in attributes.values()})
