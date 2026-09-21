"""Compose the release evidence bundle — one canonical ``report.json``.

The bundle pins the case manifest, an optional evidence receipt, the rule
catalog and the policy catalog digests, and the finding counts. It is a
canonical JSON document; ``sign`` then binds its hash to the evidence and
catalog hashes.
"""

from __future__ import annotations

import hashlib
import json
from importlib import resources
from pathlib import Path
from typing import Any

import apiforge


def canonical(payload: Any) -> str:
    """Deterministic JSON serialization — bytes identical across runs."""
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def catalog_digest() -> str:
    """sha256 over the sorted catalog YAML files — the knowledge version."""
    catalog_dir = resources.files("apiforge.rules").joinpath("catalog")
    digest = hashlib.sha256()
    for entry in sorted(catalog_dir.iterdir(), key=lambda e: str(e)):
        if str(entry).endswith(".yaml"):
            digest.update(entry.read_bytes())
    return digest.hexdigest()


class ReportError(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def build_report(
    case_dir: Path,
    receipt_path: Path | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """The evidence bundle for a persisted case (+ optional receipt)."""
    case_dir = Path(case_dir)
    manifest_path = case_dir / "case.json"
    if not manifest_path.is_file():
        raise ReportError("AF-REPORT-NO-CASE", f"no case.json under {case_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    findings_path = case_dir / "findings.json"
    findings: list[dict[str, Any]] = []
    if findings_path.is_file():
        payload = json.loads(findings_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload = payload.get("findings", [])
        if isinstance(payload, list):
            findings = [f for f in payload if isinstance(f, dict)]
    by_area: dict[str, int] = {}
    confirmed = unresolved = 0
    for finding in findings:
        status = finding.get("status")
        if status == "confirmed":
            confirmed += 1
        elif status == "unresolved":
            unresolved += 1
        rid = str(finding.get("area") or finding.get("rule_id") or "unknown")
        area = rid.split("-")[1] if "-" in rid else "unknown"
        by_area[area] = by_area.get(area, 0) + 1

    receipt: dict[str, Any] | None = None
    receipt_sha256: str | None = None
    if receipt_path is not None:
        if not Path(receipt_path).is_file():
            raise ReportError("AF-REPORT-NO-RECEIPT", str(receipt_path))
        raw = Path(receipt_path).read_text(encoding="utf-8")
        receipt = json.loads(raw)
        receipt_sha256 = sha256_text(raw)

    from apiforge.evidence.build import _policy_digest

    return {
        "report_version": 1,
        "tool_version": apiforge.__version__,
        "case_id": manifest.get("case_id"),
        "case_dir": str(case_dir),
        "artifacts": manifest.get("artifacts", {}),
        "input_hashes": manifest.get("input_hashes", {}),
        "receipt": receipt,
        "receipt_sha256": receipt_sha256,
        "catalog_sha256": catalog_digest(),
        "policy_sha256": _policy_digest(),
        "findings": {
            "total": len(findings),
            "confirmed": confirmed,
            "unresolved": unresolved,
            "by_area": dict(sorted(by_area.items())),
        },
        "emitted_at": now,
    }
