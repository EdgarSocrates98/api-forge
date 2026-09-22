"""Ed25519 key support for report signing.

A signature over the canonical signature block binds the report to whoever
holds the private key — that is key possession, not identity. Keys are PEM
files on disk; the private key is never read for verification and never
leaves the keys directory.
"""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from apiforge.report.bundle import ReportError, canonical


def generate_keypair(keys_dir: Path, name: str) -> dict[str, str]:
    """Write `<name>.pem` (private) and `<name>.pub.pem` (public)."""
    keys_dir = Path(keys_dir)
    keys_dir.mkdir(parents=True, exist_ok=True)
    private_path = keys_dir / f"{name}.pem"
    public_path = keys_dir / f"{name}.pub.pem"
    if private_path.exists() or public_path.exists():
        raise ReportError("AF-KEY-EXISTS", f"key {name!r} already exists in {keys_dir}")
    key = Ed25519PrivateKey.generate()
    private_path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    return {
        "private": str(private_path),
        "public": str(public_path),
        "public_key_sha256": public_key_fingerprint(public_path),
    }


def public_key_fingerprint(public_path: Path) -> str:
    """sha256 of the PEM bytes — the key's stable identity in reports."""
    return hashlib.sha256(Path(public_path).read_bytes()).hexdigest()


def _public_pem(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def private_key_fingerprint(private_path: Path) -> str:
    """Fingerprint of the public key derived from a private PEM."""
    key = serialization.load_pem_private_key(Path(private_path).read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ReportError("AF-KEY-NOT-ED25519", f"{private_path} is not Ed25519")
    return hashlib.sha256(_public_pem(key.public_key())).hexdigest()


def sign_payload(private_path: Path, signature_block: dict[str, Any]) -> str:
    """Ed25519 signature (b64) over the canonical hash-binding block."""
    key = serialization.load_pem_private_key(Path(private_path).read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ReportError("AF-KEY-NOT-ED25519", f"{private_path} is not Ed25519")
    signed = key.sign(canonical(signature_block).encode("utf-8"))
    return base64.b64encode(signed).decode("ascii")


def verify_payload(public_path: Path, signature_block: dict[str, Any], signature_b64: str) -> bool:
    """True only when the signature verifies against the public key."""
    try:
        key = serialization.load_pem_public_key(Path(public_path).read_bytes())
        if not isinstance(key, Ed25519PublicKey):
            return False
        key.verify(
            base64.b64decode(signature_b64),
            canonical(signature_block).encode("utf-8"),
        )
    except Exception:  # noqa: BLE001 - any failure means the signature does not hold
        return False
    return True
