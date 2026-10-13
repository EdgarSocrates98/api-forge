"""OTel JSON fixture adapter."""

import json
from collections.abc import Iterable, Mapping
from pathlib import Path


def read(path: Path) -> Iterable[Mapping[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("records") or payload.get("spans") or payload.get("data") or []
    return tuple(item for item in payload if isinstance(item, Mapping))
