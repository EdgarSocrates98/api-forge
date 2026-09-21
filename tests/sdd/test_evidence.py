"""`sdd evidence` — derive gate evidence files from real artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.sdd.evidence import emit_evidence
from apiforge.sdd.models import SddError
from apiforge.sdd.service import set_phase
from apiforge.sdd.stamp import stamp


def _feature(tmp_path: Path) -> Path:
    root = tmp_path / "docs" / "sdd"
    feature = root / "GATED"
    feature.mkdir(parents=True)
    (feature / "discover.md").write_text(
        "---\nsdd: 1\nfeature: GATED\nphase: discover\nprofile: quick\nstatus: ready\n"
        "---\n# d\n",
        encoding="utf-8",
    )
    (feature / "verify.md").write_text(
        "---\nsdd: 1\nfeature: GATED\nphase: verify\nprofile: quick\nstatus: draft\n"
        'upstream:\n  path: discover.md\n  sha256: "0"\nresults: []\n---\n# v\n',
        encoding="utf-8",
    )
    stamp(feature / "verify.md", feature / "discover.md")
    return root


def test_test_results_evidence_unblocks_gate(tmp_path: Path) -> None:
    root = _feature(tmp_path)
    pytest_out = tmp_path / "pytest.txt"
    pytest_out.write_text("490 passed, 1 skipped in 18.59s\n", encoding="utf-8")
    state = tmp_path / "state"
    payload = emit_evidence(
        root, "GATED", "test.results", pytest_out,
        "2026-09-21T00:00:00Z", state_dir=state,
    )
    assert payload["extracted"] == {"passed": 490, "failed": 0, "skipped": 1, "error": 0}
    assert Path(payload["evidence_file"]).is_file()
    # the gate now passes without an override
    change = set_phase(
        root, "GATED", "verify", "ready", strict=True,
        evidence_dir=state / "evidence", state_dir=state,
    )
    assert change.status == "ready" and not change.overrides_applied


def test_plan_tasks_extracts_task_ids(tmp_path: Path) -> None:
    root = _feature(tmp_path)
    plan = tmp_path / "plan.md"
    plan.write_text(
        "---\nsdd: 1\ntasks:\n  - id: A1\n    status: done\n"
        "  - id: A2\n    status: pending\n---\n# p\n",
        encoding="utf-8",
    )
    payload = emit_evidence(
        root, "GATED", "plan.tasks", plan, "2026-09-21T00:00:00Z",
        state_dir=tmp_path / "state",
    )
    assert payload["extracted"]["tasks"] == [
        {"id": "A1", "status": "done"},
        {"id": "A2", "status": "pending"},
    ]


def test_unknown_kind_refused(tmp_path: Path) -> None:
    root = _feature(tmp_path)
    src = tmp_path / "x.json"
    src.write_text("{}", encoding="utf-8")
    with pytest.raises(SddError, match="AF-SDD-EVIDENCE-KIND"):
        emit_evidence(root, "GATED", "made.up", src, "2026-09-21T00:00:00Z")


def test_unreadable_source_named(tmp_path: Path) -> None:
    root = _feature(tmp_path)
    with pytest.raises(SddError, match="AF-SDD-EVIDENCE-SOURCE"):
        emit_evidence(
            root, "GATED", "test.results", tmp_path / "gone.txt", "2026-09-21T00:00:00Z"
        )


def test_test_results_without_tally_refused(tmp_path: Path) -> None:
    root = _feature(tmp_path)
    src = tmp_path / "log.txt"
    src.write_text("no counts here\n", encoding="utf-8")
    with pytest.raises(SddError, match="AF-SDD-EVIDENCE-EXTRACT"):
        emit_evidence(
            root, "GATED", "test.results", src, "2026-09-21T00:00:00Z",
            state_dir=tmp_path / "state",
        )


def test_evidence_records_source_hash(tmp_path: Path) -> None:
    root = _feature(tmp_path)
    src = tmp_path / "receipt.json"
    src.write_text('{"a": 1}\n', encoding="utf-8")
    payload = emit_evidence(
        root, "GATED", "release.receipt", src, "2026-09-21T00:00:00Z",
        state_dir=tmp_path / "state",
    )
    stored = json.loads(Path(payload["evidence_file"]).read_text())
    assert stored["source_sha256"] == payload["source_sha256"]
    assert stored["kind"] == "release.receipt"
