"""Artifact dump writer shared by collectors."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import apiforge


class CollectError(Exception):
    """Named refusal from a collector."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def write_artifact(out_dir: Path, name: str, payload: Any) -> tuple[str, str]:
    """Write ``name`` under ``out_dir`` as canonical JSON; return (name, sha256)."""
    if not name.endswith(".json") or "/" in name or "\\" in name or name.startswith("."):
        raise CollectError("AF-COLLECT-PATH", f"artifact name {name!r} is not a plain *.json file")
    out_dir.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    (out_dir / name).write_text(body, encoding="utf-8")
    return name, digest


@dataclass
class CollectManifest:
    """What a collect run produced — the receipt for the dump directory."""

    source: str
    collected_at: str | None
    artifacts: dict[str, str] = field(default_factory=dict)
    tool_version: str = apiforge.__version__
    meta: dict[str, Any] = field(default_factory=dict)

    def record(self, name: str, digest: str) -> None:
        self.artifacts[name] = digest

    def write(self, out_dir: Path) -> Path:
        payload = {
            "artifacts": self.artifacts,
            "collected_at": self.collected_at,
            "meta": self.meta,
            "source": self.source,
            "tool_version": self.tool_version,
        }
        name, _ = write_artifact(out_dir, "manifest.json", payload)
        return out_dir / name
