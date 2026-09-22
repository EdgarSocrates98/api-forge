"""Optional descriptor-set loader boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def descriptor_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_descriptor_set(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(path)
    digest = descriptor_digest(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {"path": str(path), "sha256": digest, "supported": False, "reason": "binary descriptor requires optional protobuf runtime"}
    if not isinstance(payload, dict):
        return {"path": str(path), "sha256": digest, "supported": False, "reason": "descriptor JSON must be an object"}
    return {"path": str(path), "sha256": digest, "supported": True, "descriptor": payload}
