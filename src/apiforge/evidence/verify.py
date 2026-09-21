"""Verify a receipt by re-hashing every artifact it lists."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.evidence.models import Receipt


def verify_receipt(receipt: Receipt | Path | str, root: Path | None = None) -> dict[str, Any]:
    """Re-hash listed artifacts under `root` (defaults to `receipt.case`)."""
    if not isinstance(receipt, Receipt):
        data = json.loads(Path(receipt).read_text(encoding="utf-8"))
        receipt = Receipt.model_validate(data)
    base = Path(root) if root is not None else Path(receipt.case)
    mismatches: list[dict[str, str]] = []
    checked = 0
    for artifact in receipt.artifacts:
        target = base / artifact.path
        if not target.is_file():
            mismatches.append(
                {
                    "code": "AF-EVIDENCE-MISSING",
                    "path": artifact.path,
                    "detail": "listed artifact is absent",
                }
            )
            continue
        checked += 1
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != artifact.sha256:
            mismatches.append(
                {
                    "code": "AF-EVIDENCE-MISMATCH",
                    "path": artifact.path,
                    "detail": f"expected {artifact.sha256}, found {actual}",
                }
            )
    return {
        "ok": not mismatches,
        "checked": checked,
        "mismatches": mismatches,
        "proves": receipt.proves,
    }
