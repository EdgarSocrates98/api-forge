"""Content-addressed ctx store under ``<root>/.apiforge/ctx``; reads verify the hash."""

from __future__ import annotations

import re
from pathlib import Path

from apiforge.context.gateway.canonical import CTX_PREFIX, normalize, uri_for
from apiforge.context.gateway.errors import GatewayError

_URI = re.compile(r"^ctx://sha256/([0-9a-f]{64})$")


class CtxStore:
    """Immutable objects named by the sha256 of their LF-normalized text."""

    def __init__(self, root: Path) -> None:
        self.dir = Path(root) / ".apiforge" / "ctx"

    def put(self, content: str) -> str:
        uri = uri_for(content)
        path = self._path(uri)
        if not path.is_file():
            self.dir.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(path.name + ".tmp")
            tmp.write_text(normalize(content), encoding="utf-8", newline="\n")
            tmp.replace(path)
        return uri

    def exists(self, uri: str) -> bool:
        return self._path(uri).is_file()

    def get(self, uri: str) -> str:
        path = self._path(uri)
        if not path.is_file():
            raise GatewayError(
                "AF-CTX-REF-NOT-FOUND",
                f"{uri} is not in {self.dir}",
                field="uri",
                unlock="rebuild the capsule with `apiforge context capsule` in the same root",
            )
        content = path.read_text(encoding="utf-8")
        if uri_for(content) != uri:
            raise GatewayError(
                "AF-CTX-HASH-MISMATCH",
                f"{path} no longer hashes to {uri}",
                field="uri",
                unlock="delete the tampered object and rebuild the capsule",
            )
        return content

    def _path(self, uri: str) -> Path:
        match = _URI.match(uri)
        if match is None:
            raise GatewayError(
                "AF-CTX-REF-INVALID",
                f"{uri!r} is not a {CTX_PREFIX}<64 hex> reference",
                field="uri",
                unlock="pass a ref exactly as emitted by `apiforge context capsule`",
            )
        return self.dir / match.group(1)


__all__ = ["CtxStore"]
