"""Canonical bytes and content addressing shared by the gateway and its store."""

from __future__ import annotations

import hashlib
import json
from typing import Any

CTX_PREFIX = "ctx://sha256/"


def dumps(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def digest(text: str) -> str:
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()


def uri_for(text: str) -> str:
    return CTX_PREFIX + digest(text)


__all__ = ["CTX_PREFIX", "digest", "dumps", "normalize", "uri_for"]
