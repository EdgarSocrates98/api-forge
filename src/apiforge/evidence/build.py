"""Emit a receipt over a persisted case directory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.evidence.models import Receipt, ReceiptArtifact
from apiforge.policy.loader import DEFAULT_POLICY


class EvidenceError(RuntimeError):
    def __init__(self, code: str, detail: str, field: str | None = None) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.field = field


def _policy_digest() -> str:
    canonical = json.dumps(
        DEFAULT_POLICY.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def emit_receipt(case_dir: Path, now: str | None = None) -> Receipt:
    """Receipt over `case.json` + artifacts. `now` is the only clock source."""
    case_dir = Path(case_dir)
    manifest_path = case_dir / "case.json"
    if not manifest_path.is_file():
        raise EvidenceError(
            "AF-EVIDENCE-NO-CASE",
            f"no case.json under {case_dir}",
            field="case",
        )
    manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts: list[ReceiptArtifact] = []
    for kind, ref in sorted(manifest.get("artifacts", {}).items()):
        if not isinstance(ref, dict):
            continue
        path = ref.get("path")
        artifact = case_dir / str(path)
        if not artifact.is_file():
            raise EvidenceError(
                "AF-EVIDENCE-MISSING",
                f"manifest artifact {path} is absent from {case_dir}",
                field="artifacts",
            )
        actual = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if actual != ref.get("sha256"):
            raise EvidenceError(
                "AF-EVIDENCE-MISMATCH",
                f"{path}: manifest sha256 {ref.get('sha256')} != file {actual}",
                field="artifacts",
            )
        artifacts.append(
            ReceiptArtifact(path=str(path), sha256=actual, kind=str(kind))
        )
    inputs = manifest.get("input_hashes", {})
    return Receipt(
        case=str(case_dir),
        policy_sha256=_policy_digest(),
        artifacts=tuple(artifacts),
        input_hashes=tuple(sorted((str(k), str(v)) for k, v in inputs.items())),
        emitted_at=now,
    )
