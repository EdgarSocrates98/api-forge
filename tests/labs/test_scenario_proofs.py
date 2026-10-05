from __future__ import annotations

from pathlib import Path

import yaml

PROOF_DIR = Path(__file__).parent / "proofs"


def test_declared_lab_proofs_have_explicit_scope_and_expectation() -> None:
    proofs = sorted(PROOF_DIR.glob("*.yaml"))
    assert len(proofs) == 5
    for path in proofs:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["status"] == "covered"
        assert data["kind"]
        assert data["input"]
        assert data["expected"]
        assert "deterministic" in data["evidence"]
        assert "claim" in data["evidence"]
