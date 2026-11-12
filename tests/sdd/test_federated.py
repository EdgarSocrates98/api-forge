"""Federated SDD adapter tests — Onda 5B (apiforge)."""

from __future__ import annotations

from apiforge.sdd import federated
from apiforge.sdd.models import SddIssue


def test_phase_map_covers_native_phases():
    for native in (
        "discover",
        "intent",
        "contract",
        "architecture",
        "plan",
        "build",
        "verify",
        "secure",
        "benchmark",
        "ship",
    ):
        assert federated.map_phase(native) in (
            "explore",
            "define",
            "design",
            "plan",
            "build_report",
            "verify",
            "ship",
            "learn",
        )


def test_gate_from_sdd_issues():
    refused = [
        SddIssue(
            code="AF-SDD-PHASE-ORDER",
            feature="F1",
            message="upstream ahead",
            phase="plan",
            field="upstream",
            unlock="reorder artifacts",
        )
    ]
    gate = federated.to_gate("F1", "plan", {"refused": refused, "unresolved": []})
    assert gate["schema"] == "forge/SDDGate/v1"
    assert gate["phase"] == "plan"
    assert gate["ok"] is False
    item = gate["refused"][0]
    assert item["code"] == "AF-SDD-PHASE-ORDER"
    assert item["field"] == "upstream"
    assert item["unlock"] == "reorder artifacts"


def test_gate_ok_when_clean():
    gate = federated.to_gate("F1", "verify", {"ok": True, "refused": [], "unresolved": []})
    assert gate["ok"] is True


def test_receipt_override_carries_actor():
    r = federated.to_receipt(
        "F1",
        "ship",
        "release",
        "owner",
        "2026-04-05T10:00:00Z",
        verdict="overridden",
        override={"reason": "hotfix accepted", "actor": "owner", "undispensable": False},
    )
    assert r["override"]["actor"] == "owner"


def test_evidence_computes_sha(tmp_path):
    f = tmp_path / "out.log"
    f.write_text("run")
    ev = federated.to_evidence(f, kind="test-run", agent="t", command=["pytest"])
    assert ev["sha256"].startswith("sha256:")


def test_federated_view_empty(tmp_path):
    assert federated.federated_view(tmp_path, feature="F1") == {}
