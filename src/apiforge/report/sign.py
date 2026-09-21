"""Sign and verify a report — hash-bound correspondence; optional key binding.

The signature block pins three digests: the report body (minus the
signature), the evidence receipt, and the rule catalog at sign time.
``verify`` recomputes each and names every part that diverged.

With ``--key`` the block additionally carries an Ed25519 signature over the
canonical hash-binding block plus the signing key's fingerprint — that
proves the report was signed by whoever holds the key, never identity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.report.bundle import ReportError, canonical, catalog_digest, sha256_text

SIGNATURE_VERSION = 1


def sign_report(report: dict[str, Any], key_path: Path | None = None) -> dict[str, Any]:
    """Append the signature block; the input report is copied, not mutated."""
    body = {k: v for k, v in report.items() if k != "signature"}
    signature: dict[str, Any] = {
        "version": SIGNATURE_VERSION,
        "body_sha256": sha256_text(canonical(body)),
        "evidence_sha256": body.get("receipt_sha256"),
        "catalog_sha256": catalog_digest(),
    }
    if key_path is not None:
        from apiforge.report.keys import private_key_fingerprint, sign_payload

        signature["algorithm"] = "ed25519"
        signature["public_key_sha256"] = private_key_fingerprint(Path(key_path))
        signature["signature_b64"] = sign_payload(Path(key_path), signature)
    return {**body, "signature": signature}


def verify_report(
    report: dict[str, Any],
    receipt_path: Path | None = None,
    pubkey_path: Path | None = None,
) -> dict[str, Any]:
    """Name every part that diverged; ``ok`` is the absence of divergence."""
    signature = report.get("signature")
    if not isinstance(signature, dict):
        raise ReportError("AF-REPORT-UNSIGNED", "report carries no signature block")
    diverged: list[str] = []
    crypto = "absent"

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

    signature_b64 = signature.get("signature_b64")
    if signature_b64:
        if pubkey_path is None:
            crypto = "unverified"
        else:
            from apiforge.report.keys import public_key_fingerprint, verify_payload

            expected_fp = signature.get("public_key_sha256")
            if expected_fp and expected_fp != public_key_fingerprint(pubkey_path):
                diverged.append("signature_key")
                crypto = "invalid"
            else:
                signed_block = {
                    k: v
                    for k, v in signature.items()
                    if k not in ("signature_b64",)
                }
                if verify_payload(pubkey_path, signed_block, str(signature_b64)):
                    crypto = "valid"
                else:
                    diverged.append("signature_crypto")
                    crypto = "invalid"

    return {
        "ok": not diverged,
        "diverged": sorted(set(diverged)),
        "signature": signature,
        "crypto": crypto,
    }
