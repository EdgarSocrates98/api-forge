"""Ed25519 report signing: keygen, sign --key, verify --pubkey."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.report.bundle import ReportError
from apiforge.report.keys import generate_keypair
from apiforge.report.sign import sign_report, verify_report


def _report() -> dict:
    return {"case_id": "case:x", "findings": {"confirmed": 1}, "receipt_sha256": None}


def test_keygen_writes_pair(tmp_path: Path) -> None:
    out = generate_keypair(tmp_path / "keys", "release")
    assert Path(out["private"]).is_file()
    assert Path(out["public"]).is_file()
    assert len(out["public_key_sha256"]) == 64
    with pytest.raises(ReportError, match="AF-KEY-EXISTS"):
        generate_keypair(tmp_path / "keys", "release")


def test_signed_report_verifies_with_pubkey(tmp_path: Path) -> None:
    keys = generate_keypair(tmp_path / "keys", "release")
    signed = sign_report(_report(), key_path=Path(keys["private"]))
    sig = signed["signature"]
    assert sig["algorithm"] == "ed25519"
    assert sig["signature_b64"]
    result = verify_report(signed, pubkey_path=Path(keys["public"]))
    assert result["ok"] is True
    assert result["crypto"] == "valid"


def test_unsigned_key_mode_stays_hash_only(tmp_path: Path) -> None:
    signed = sign_report(_report())
    assert "signature_b64" not in signed["signature"]
    assert verify_report(signed)["crypto"] == "absent"


def test_tampered_body_diverges_body_not_crypto(tmp_path: Path) -> None:
    """The signature covers the hash-pinning block; tampering the body shows
    as `body` divergence while the pin block itself still verifies."""
    keys = generate_keypair(tmp_path / "keys", "release")
    signed = sign_report(_report(), key_path=Path(keys["private"]))
    tampered = json.loads(json.dumps(signed))
    tampered["findings"]["confirmed"] = 99
    result = verify_report(tampered, pubkey_path=Path(keys["public"]))
    assert result["ok"] is False
    assert "body" in result["diverged"]
    assert "signature_crypto" not in result["diverged"]


def test_tampered_signature_block_diverges_crypto(tmp_path: Path) -> None:
    keys = generate_keypair(tmp_path / "keys", "release")
    signed = sign_report(_report(), key_path=Path(keys["private"]))
    tampered = json.loads(json.dumps(signed))
    tampered["signature"]["signature_b64"] = "A" + tampered["signature"]["signature_b64"][1:]
    result = verify_report(tampered, pubkey_path=Path(keys["public"]))
    assert result["ok"] is False
    assert result["diverged"] == ["signature_crypto"]


def test_wrong_pubkey_is_named(tmp_path: Path) -> None:
    a = generate_keypair(tmp_path / "ka", "a")
    b = generate_keypair(tmp_path / "kb", "b")
    signed = sign_report(_report(), key_path=Path(a["private"]))
    result = verify_report(signed, pubkey_path=Path(b["public"]))
    assert result["ok"] is False
    assert "signature_key" in result["diverged"]


def test_signed_without_pubkey_reports_unverified(tmp_path: Path) -> None:
    keys = generate_keypair(tmp_path / "keys", "release")
    signed = sign_report(_report(), key_path=Path(keys["private"]))
    result = verify_report(signed)
    assert result["crypto"] == "unverified"
    assert result["ok"] is True  # hash parts still hold
