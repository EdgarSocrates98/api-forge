import hashlib
import json
from pathlib import Path

from apiforge.evidence.build import emit_receipt
from apiforge.evidence.verify import verify_receipt


def _make_case(tmp_path: Path) -> Path:
    case = tmp_path / "case"
    case.mkdir()
    facts = {"facts": []}
    (case / "facts.json").write_text(json.dumps(facts), encoding="utf-8")
    digest = hashlib.sha256(json.dumps(facts).encode()).hexdigest()
    manifest = {
        "schema_version": "1",
        "case_id": "case:test",
        "artifacts": {"facts": {"path": "facts.json", "sha256": digest}},
        "input_hashes": {"contract:c.yaml": "0" * 64},
    }
    (case / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
    return case


def test_receipt_emits_hashes_and_verifies(tmp_path: Path) -> None:
    case = _make_case(tmp_path)
    receipt = emit_receipt(case)
    assert receipt.artifacts[0].path == "facts.json"
    assert len(receipt.policy_sha256) == 64
    assert receipt.emitted_at is None
    report = verify_receipt(receipt, root=case)
    assert report["ok"] is True


def test_receipt_is_deterministic(tmp_path: Path) -> None:
    case = _make_case(tmp_path)
    a = emit_receipt(case).model_dump(mode="json")
    b = emit_receipt(case).model_dump(mode="json")
    assert a == b


def test_emitted_at_only_when_requested(tmp_path: Path) -> None:
    case = _make_case(tmp_path)
    receipt = emit_receipt(case, now="2026-09-21T00:00:00Z")
    assert receipt.emitted_at == "2026-09-21T00:00:00Z"


def test_tampered_artifact_is_detected(tmp_path: Path) -> None:
    case = _make_case(tmp_path)
    receipt = emit_receipt(case)
    (case / "facts.json").write_text('{"facts": [1]}', encoding="utf-8")
    report = verify_receipt(receipt, root=case)
    assert report["ok"] is False
    assert report["mismatches"][0]["code"] == "AF-EVIDENCE-MISMATCH"


def test_missing_artifact_is_named(tmp_path: Path) -> None:
    case = _make_case(tmp_path)
    receipt = emit_receipt(case)
    (case / "facts.json").unlink()
    report = verify_receipt(receipt, root=case)
    assert report["mismatches"][0]["code"] == "AF-EVIDENCE-MISSING"
