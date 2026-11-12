"""Federated contract conformance — adapter output vs canonical schemas.

Canonical JSON Schemas live in the the-forge workspace sibling; outside
a full FORJAS workspace this test skips (absence reported, not faked).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

_SCHEMA_CANDIDATES = [
    os.environ.get("FORGE_SDD_SCHEMA_DIR", ""),
    str(Path(__file__).resolve().parents[3] / "the-forge" / "docs"
        / "portable-installation" / "schemas"),
]


def _schema_dir() -> Path:
    for cand in _SCHEMA_CANDIDATES:
        p = Path(cand) if cand else Path("/nonexistent")
        if p.is_dir() and (p / "ForgeSDDGate.schema.json").is_file():
            return p
    pytest.skip("canonical schema dir not available in this workspace")
    raise AssertionError


def _load(name: str) -> dict:
    return json.loads((_schema_dir() / name).read_text(encoding="utf-8"))


def test_gate_conforms():
    from apiforge.sdd import federated
    from apiforge.sdd.models import SddIssue
    gate = federated.to_gate("F1", "contract", {
        "refused": [SddIssue(code="AF-SDD-PHASE-ORDER", feature="F1",
                             message="m", phase="plan", field="up",
                             unlock="reorder")],
        "unresolved": []})
    jsonschema.validate(gate, _load("ForgeSDDGate.schema.json"))


def test_receipt_conforms():
    from apiforge.sdd import federated
    r = federated.to_receipt("F1", "verify", "pytest", "verifier",
                             "2026-04-05T10:00:00Z", verdict="pass",
                             outputs=["junit.xml"])
    jsonschema.validate(r, _load("ForgeSDDReceipt.schema.json"))


def test_evidence_conforms(tmp_path):
    from apiforge.sdd import federated
    f = tmp_path / "e.txt"
    f.write_text("x")
    ev = federated.to_evidence(f, kind="test-run", agent="t",
                               command=["pytest"], covers=["REQ-1"])
    jsonschema.validate(ev, _load("ForgeEvidence.schema.json"))
