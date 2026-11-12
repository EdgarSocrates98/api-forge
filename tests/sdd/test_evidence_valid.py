"""Evidence validator — existence alone never approves."""

from __future__ import annotations

import hashlib
import json

import pytest

from apiforge.sdd.evidence_valid import validate_evidence


def _src(tmp_path, text="src"):
    p = tmp_path / "source.txt"
    p.write_text(text)
    return p


def _w(tmp_path, doc, src_text="src"):
    src = _src(tmp_path, src_text)
    doc.setdefault("kind", "test.results")
    doc.setdefault("source_sha256",
                   hashlib.sha256(src.read_bytes()).hexdigest())
    doc.setdefault("recorded_at", "2026-09-21T00:00:00Z")
    doc.setdefault("source_path", str(src))
    p = tmp_path / "test.results.json"
    p.write_text(json.dumps(doc))
    return p


def test_absent_is_invalid(tmp_path):
    v = validate_evidence(tmp_path / "tests.json", feature="F1")
    assert v["state"] == "invalid"
    assert "ABSENT" in v["code"]


def test_unreadable_invalid(tmp_path):
    p = tmp_path / "tests.json"
    p.write_text("{not json")
    assert validate_evidence(p, feature="F1")["state"] == "invalid"


def test_missing_required_inconclusive(tmp_path):
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"kind": "test.results"}))
    assert validate_evidence(p, feature="F1")["state"] == "inconclusive"


def test_wrong_feature_invalid(tmp_path):
    p = _w(tmp_path, {"feature": "OTHER", "status": "passed"})
    v = validate_evidence(p, feature="F1")
    assert v["state"] == "invalid"
    assert "FEATURE" in v["code"]


def test_wrong_kind_invalid(tmp_path):
    p = _w(tmp_path, {"kind": "security", "status": "passed"})
    v = validate_evidence(p, feature="F1", expected_kind="test.results")
    assert v["state"] == "invalid"


def test_stale_source_invalid(tmp_path):
    p = _w(tmp_path, {"status": "passed"})
    (tmp_path / "source.txt").write_text("changed")
    v = validate_evidence(p, feature="F1")
    assert v["state"] == "invalid"
    assert "STALE" in v["code"]


def test_failed_tests_invalid(tmp_path):
    """The '10 passed, 50 failed' hole — failed>0 must never pass."""
    p = _w(tmp_path, {"extracted": {"passed": 10, "failed": 50}})
    v = validate_evidence(p, feature="F1")
    assert v["state"] == "invalid"
    assert "FAILED" in v["code"]


def test_zero_passed_inconclusive(tmp_path):
    p = _w(tmp_path, {"extracted": {"passed": 0, "failed": 0, "skipped": 3}})
    assert validate_evidence(p, feature="F1")["state"] == "inconclusive"


def test_passing_tests_valid(tmp_path):
    p = _w(tmp_path, {"feature": "F1",
                      "extracted": {"passed": 12, "failed": 0}})
    assert validate_evidence(p, feature="F1")["state"] == "valid"


def test_failed_status_invalid(tmp_path):
    p = _w(tmp_path, {"kind": "security", "status": "violated"})
    assert validate_evidence(p, feature="F1")["state"] == "invalid"


def test_set_phase_evidence_enforced(tmp_path):
    """E2E: strict set-phase refuses on an evidence file that exists but
    records a failed run."""
    from apiforge.sdd.models import SddError, load_gates
    from apiforge.sdd.service import set_phase

    feat = tmp_path / "FEAT"
    feat.mkdir()
    (feat / "verify.md").write_text("---\nstatus: draft\n---\n# verify\n")
    ev = tmp_path / ".apiforge" / "sdd" / "FEAT" / "evidence"
    ev.mkdir(parents=True)
    gates = [g for g in load_gates() if "verify" in g.guards_phases]
    if not gates:
        pytest.skip("no gate guards verify in gates.yaml")
    src = tmp_path / "run.txt"
    src.write_text("5 passed, 3 failed")
    for g in gates:
        (ev / f"{g.satisfied_by}.json").write_text(json.dumps(
            {"schema": "x", "kind": g.satisfied_by,
             "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
             "recorded_at": "t", "source_path": str(src),
             "extracted": {"passed": 5, "failed": 3}}))
    with pytest.raises(SddError):
        set_phase(tmp_path, "FEAT", "verify", "ready", strict=True,
                  evidence_dir=ev,
                  state_dir=tmp_path / ".apiforge" / "sdd" / "FEAT")
