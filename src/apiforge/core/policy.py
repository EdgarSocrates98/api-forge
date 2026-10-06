"""§86 policy anchors: receipts name the exact rules they were decided under.

A receipt that only says *what* was decided cannot be audited for drift —
the same decision under a different policy is a different decision. Every
governed receipt may carry ``policy_id`` / ``policy_version`` /
``policy_hash`` so the verdict binds to content, not to a file name.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.core.io import sha256_file


def policy_descriptor(path: Path, *, policy_id: str | None = None) -> dict[str, Any]:
    """Describe one rules file: declared version plus a content hash.

    ``policy_version`` prefers the file's declared ``schema`` tag and falls
    back to a ``version`` field; a missing file or unreadable YAML is
    reported honestly (``hash=unavailable`` / ``version=undeclared``)
    rather than aborting the caller — receipts must still be emitted.
    """
    target = Path(path)
    version: str | None = None
    try:
        raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
        if isinstance(raw, dict):
            if raw.get("schema"):
                version = str(raw["schema"])
            elif raw.get("version") is not None:
                version = f"v{raw['version']}"
    except (OSError, yaml.YAMLError):
        version = None
    try:
        digest = f"sha256:{sha256_file(target)}"
    except OSError:
        digest = "unavailable"
    return {
        "policy_id": policy_id or target.stem,
        "policy_version": version or "undeclared",
        "policy_hash": digest,
    }


__all__ = ["policy_descriptor"]
