"""Deterministic artifact IO: streaming SHA-256 and atomic stable JSON."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

_BLOCK = 1 << 20
_WINDOWS_REPLACE_RETRIES = 6
_WINDOWS_REPLACE_ERRORS = {5, 32}  # access denied / sharing violation


def sha256_file(path: Path) -> str:
    """Return the hex SHA-256 of a file, read in 1 MiB blocks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(_BLOCK), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(path: Path) -> str:
    """SHA-256 of a text file with CRLF normalized to LF.

    Text artifacts are hashed on their logical content: a checkout that only
    differs in line endings produces the same digest.
    """
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _to_jsonable(value: object) -> object:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


def _replace_with_retry(source: Path, target: Path) -> None:
    """Publish an artifact despite short-lived Windows sharing violations."""
    attempts = _WINDOWS_REPLACE_RETRIES if os.name == "nt" else 1
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except OSError as exc:
            winerror = getattr(exc, "winerror", None)
            if (
                os.name != "nt"
                or winerror not in _WINDOWS_REPLACE_ERRORS
                or attempt == attempts - 1
            ):
                raise
            time.sleep(min(0.02 * (2**attempt), 0.25))


def atomic_write_text(path: Path, text: str) -> Path:
    """Write UTF-8 text through a unique sibling and atomically publish it."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=target.parent, suffix=".tmp", prefix=f".{target.name}.")
    temporary = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        _replace_with_retry(temporary, target)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return target


def write_json(path: Path, value: object) -> None:
    """Write canonical JSON: sorted keys, indent 2, UTF-8, one trailing newline.

    The payload is serialized next to the target and moved into place with
    `os.replace`, so a reader never sees a partial artifact.
    """
    payload = json.dumps(_to_jsonable(value), sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    atomic_write_text(Path(path), payload)


def read_json(path: Path) -> Any:
    """Read a UTF-8 JSON artifact, returning plain Python values."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)
