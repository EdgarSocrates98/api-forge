"""Deterministic identifiers for JSON-compatible evidence."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from math import isfinite


def _require_json_value(value: object) -> None:
    if value is None or isinstance(value, str | bool | int):
        return
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError("stable IDs require JSON-compatible finite numbers")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("stable IDs require JSON-compatible string object keys")
            _require_json_value(item)
        return
    if isinstance(value, list | tuple):
        for item in value:
            _require_json_value(item)
        return
    raise ValueError(f"stable IDs require JSON-compatible values, got {type(value).__name__}")


def stable_id(prefix: str, value: object) -> str:
    """Return a short SHA-256 identifier for a canonical JSON value."""

    _require_json_value(value)
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()[:16]
    return f"{prefix}:{digest}"
