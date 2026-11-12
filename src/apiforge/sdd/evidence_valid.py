"""Evidence validation — an evidence *file existing* never unlocks a gate.

Classifies receipts as ``invalid`` / ``inconclusive`` / ``valid``:
- invalid       → unreadable, wrong shape, wrong feature/kind, failed
                  outcome, or a tampered source (hash mismatch)
- inconclusive  → missing fields, vanished source, unknown format
- valid         → receipt whose recorded outcome passes *and* whose
                  source hash still matches the file on disk
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from apiforge.core.io import read_json

#: fields every evidence receipt must carry (matches emit_evidence shape)
REQUIRED = ("kind", "source_sha256", "recorded_at")


def validate_evidence(
    path: Path, *, feature: str, expected_kind: str | None = None
) -> dict[str, Any]:
    """Validate one evidence receipt → {state, code, reason}."""
    if not path.is_file():
        return {
            "state": "invalid",
            "code": "AF-SDD-EVIDENCE-ABSENT",
            "reason": f"{path.name} does not exist",
        }
    try:
        doc = read_json(path)
    except Exception:  # noqa: BLE001 — any parse failure is "unreadable"
        return {
            "state": "invalid",
            "code": "AF-SDD-EVIDENCE-UNREADABLE",
            "reason": f"{path.name} is not parseable JSON",
        }
    if not isinstance(doc, dict):
        return {
            "state": "invalid",
            "code": "AF-SDD-EVIDENCE-SHAPE",
            "reason": "receipt is not a JSON object",
        }
    missing = [k for k in REQUIRED if k not in doc]
    if missing:
        return {
            "state": "inconclusive",
            "code": "AF-SDD-EVIDENCE-INCOMPLETE",
            "reason": f"receipt lacks fields: {','.join(missing)}",
        }
    if expected_kind and doc.get("kind") != expected_kind:
        return {
            "state": "invalid",
            "code": "AF-SDD-EVIDENCE-KIND",
            "reason": f"kind {doc.get('kind')!r} != expected {expected_kind!r}",
        }
    feat = doc.get("feature")
    if feat is not None and feat != feature:
        return {
            "state": "invalid",
            "code": "AF-SDD-EVIDENCE-FEATURE",
            "reason": f"receipt is for feature {feat!r}, not {feature!r}",
        }

    # provenance: the recorded source hash must still match the artifact
    src = doc.get("source_path")
    recorded = doc.get("source_sha256")
    if src:
        sp = Path(src)
        if not sp.is_file():
            return {
                "state": "inconclusive",
                "code": "AF-SDD-EVIDENCE-SOURCE-GONE",
                "reason": f"source {src!r} no longer exists",
            }
        if hashlib.sha256(sp.read_bytes()).hexdigest() != recorded:
            return {
                "state": "invalid",
                "code": "AF-SDD-EVIDENCE-STALE",
                "reason": "source changed since evidence was recorded "
                "(hash mismatch) — re-run sdd evidence",
            }

    # outcome: test receipts must show a passing run — failed counts fatal
    ext = doc.get("extracted") or {}
    if isinstance(ext, dict) and any(k in ext for k in ("passed", "failed", "error", "errors")):
        if (
            int(ext.get("failed") or 0) > 0
            or int(ext.get("error") or 0) > 0
            or int(ext.get("errors") or 0) > 0
        ):
            return {
                "state": "invalid",
                "code": "AF-SDD-EVIDENCE-FAILED",
                "reason": f"test run records {ext.get('failed', 0)} failed"
                f" / {ext.get('error') or ext.get('errors') or 0}"
                " errors",
            }
        if int(ext.get("passed") or 0) <= 0:
            return {
                "state": "inconclusive",
                "code": "AF-SDD-EVIDENCE-EMPTY",
                "reason": "test run records zero passed tests",
            }
    status = doc.get("status") or doc.get("result")
    if isinstance(status, str) and status.lower() in ("failed", "error", "violated", "blocked"):
        return {
            "state": "invalid",
            "code": "AF-SDD-EVIDENCE-FAILED",
            "reason": f"receipt records status {status!r}",
        }
    return {"state": "valid", "code": "AF-SDD-EVIDENCE-OK", "reason": ""}
