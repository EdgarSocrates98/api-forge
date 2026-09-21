"""Sign and verify a report — hash-bound correspondence, never authorship.

The signature block pins three digests: the report body (minus the
signature), the evidence receipt, and the rule catalog at sign time.
``verify`` recomputes each and names every part that diverged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.report.bundle import ReportError, canonical, catalog_digest, sha256_text

SIGNATURE_VERSION = 1


def sign_report(report: dict[str, Any]) -> dict[str, Any]:
    """Append the signature block; the input report is copied, not mutated."""
    body = {k: v for k, v in report.items() if k != "signature"}
    signature = {
        "version": SIGNATURE_VERSION,
        "body_sha256": sha256_text(canonical(body)),
        "evidence_sha256": body.get("receipt_sha256"),
        "catalog_sha256": catalog_digest(),
    }
    return {**body, "signature": signature}


def verify_report(
    report: dict[str, Any], receipt_path: Path | None = None
) -> dict[str, Any]:
    """Name every part that diverged; ``ok`` is the absence of divergence."""
    signature = report.get("signature")
    if not isinstance(signature, dict):
        raise ReportError("AF-REPORT-UNSIGNED", "report carries no signature block")
    diverged: list[str] = []

    if signature.get("version") != SIGNATURE_VERSION:
        diverged.append("signature_version")

    body = {k: v for k, v in report.items() if k != "signature"}
    if signature.get("body_sha256") != sha256_text(canonical(body)):
        diverged.append("body")

    evidence_expected = signature.get("evidence_sha256")
    if evidence_expected is not None:
        evidence_actual = (
            sha256_text(Path(receipt_path).read_text(encoding="utf-8"))
            if receipt_path is not None and Path(receipt_path).is_file()
            else body.get("receipt_sha256")
        )
        if evidence_actual != evidence_expected:
            diverged.append("evidence")

    if signature.get("catalog_sha256") != catalog_digest():
        diverged.append("catalog")

    return {"ok": not diverged, "diverged": sorted(set(diverged)), "signature": signature}
