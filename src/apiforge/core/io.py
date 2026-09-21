"""Deterministic artifact IO: streaming SHA-256 and atomic stable JSON."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from pydantic import BaseModel

_BLOCK = 1 << 20


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file, read in 1 MiB blocks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(_BLOCK), b""):
            digest.update(block)
    return digest.hexdigest()


def _to_jsonable(value: object) -> object:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


def write_json(path: Path, value: object) -> None:
    """Write canonical JSON: sorted keys, indent 2, UTF-8, one trailing newline.

    The payload is serialized next to the target and moved into place with
    `os.replace`, so a reader never sees a partial artifact.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(_to_jsonable(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, suffix=".tmp", prefix=target.name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
        os.replace(tmp_name, target)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def read_json(path: Path) -> Any:
    """Read a UTF-8 JSON artifact, returning plain Python values."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)
