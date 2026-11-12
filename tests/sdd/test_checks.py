from pathlib import Path

import pytest

from apiforge.sdd.checks import check, status
from apiforge.sdd.models import SddError
from apiforge.sdd.service import set_phase
from apiforge.sdd.stamp import stamp

ROOT = Path("tests/fixtures/sdd_root")


def test_upstream_stale_is_named_with_unlock() -> None:
    report = check(ROOT)
    refusal = next(r for r in report.refused if r.code == "AF-SDD-UPSTREAM-STALE")
    assert refusal.field == "upstream.sha256"
    assert refusal.unlock and "stamp" in refusal.unlock


def test_gap_allowed_at_ready_forbidden_at_done() -> None:
    report = check(ROOT, feature="GAPPED_FEATURE")
    assert any(u.code == "AF-SDD-GAP-TEST-NOT-WRITTEN" for u in report.unresolved)
    assert not report.ok  # done requires zero gaps


def test_skipped_phase_must_be_declared() -> None:
    report = check(ROOT, feature="SILENT_SKIP")
    assert any(r.code == "AF-SDD-PHASE-SKIPPED-UNDECLARED" for r in report.refused)


def test_phase_order_is_checked() -> None:
    report = check(ROOT, feature="ORDER_BAD")
    assert any(r.code == "AF-SDD-PHASE-ORDER" for r in report.refused)


def test_unknown_feature_is_refused() -> None:
    with pytest.raises(SddError, match="AF-SDD-FEATURE-UNKNOWN"):
        check(ROOT, feature="NOPE")


def test_status_maps_phases() -> None:
    st = status(ROOT)
    assert st.features["DEMO_FEATURE"]["phases"]["discover"] == "ready"
    assert "intent" in st.features["SILENT_SKIP"]["missing_required"]


def _make_feature(tmp_path: Path) -> Path:
    root = tmp_path / "sdd"
    feature = root / "GATED"
    feature.mkdir(parents=True)
    (feature / "discover.md").write_text(
        "---\nsdd: 1\nfeature: GATED\nphase: discover\nprofile: quick\nstatus: done\n"
        "approaches: [a]\nchosen: a\n---\n# d\n",
        encoding="utf-8",
    )
    (feature / "verify.md").write_text(
        "---\nsdd: 1\nfeature: GATED\nphase: verify\nprofile: quick\nstatus: draft\n"
        'upstream:\n  path: discover.md\n  sha256: "0"\nresults: []\n---\n# v\n',
        encoding="utf-8",
    )
    stamp(feature / "verify.md", feature / "discover.md")
    return root


def test_set_phase_blocked_without_evidence(tmp_path: Path) -> None:
    root = _make_feature(tmp_path)
    with pytest.raises(SddError, match="AF-SDD-EVIDENCE-ABSENT"):
        set_phase(root, "GATED", "verify", "ready", strict=True)


def test_set_phase_allowed_with_evidence(tmp_path: Path) -> None:
    root = _make_feature(tmp_path)
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    src = tmp_path / "pytest.txt"
    src.write_text("12 passed in 0.4s\n", encoding="utf-8")
    from apiforge.sdd.evidence import emit_evidence

    emit_evidence(root, "GATED", "test.results", src, "2026-09-21T00:00:00Z", state_dir=tmp_path)
    change = set_phase(
        root, "GATED", "verify", "ready", strict=True, evidence_dir=evidence, state_dir=tmp_path
    )
    assert change.status == "ready"
    assert "status: ready" in (root / "GATED" / "verify.md").read_text(encoding="utf-8")


def test_set_phase_override_is_recorded(tmp_path: Path) -> None:
    root = _make_feature(tmp_path)
    state = tmp_path / "state"
    change = set_phase(
        root,
        "GATED",
        "verify",
        "ready",
        strict=True,
        override={"gate": "build-verified", "reason": "no tests yet", "actor": "edgar"},
        state_dir=state,
    )
    assert "build-verified" in change.overrides_applied
    import json

    record = json.loads((state / "gate-overrides.json").read_text(encoding="utf-8"))
    assert record["overrides"][0]["gate"] == "build-verified"
    assert record["overrides"][0]["reason"] == "no tests yet"


def _ship_feature(tmp_path: Path, profile: str) -> Path:
    root = tmp_path / "sdd"
    feature = root / "SHIPME"
    feature.mkdir(parents=True)
    (feature / "intent.md").write_text(
        f"---\nsdd: 1\nfeature: SHIPME\nphase: intent\nprofile: {profile}\nstatus: done\n"
        "problem: p\nsuccess: [s]\nout_of_scope: o\n---\n# i\n",
        encoding="utf-8",
    )
    (feature / "ship.md").write_text(
        "---\nsdd: 1\nfeature: SHIPME\nphase: ship\nprofile: quick\nstatus: draft\n"
        'upstream:\n  path: intent.md\n  sha256: "0"\n---\n# s\n',
        encoding="utf-8",
    )
    stamp(feature / "ship.md", feature / "intent.md")
    return root


def test_migration_gate_scoped_to_profile(tmp_path: Path) -> None:
    """migration-evidenced blocks ship only for `migration` profile."""
    from apiforge.sdd.evidence import emit_evidence

    root = _ship_feature(tmp_path, "migration")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    # release.receipt present → the only thing left blocking is migration.plan
    receipt = tmp_path / "receipt.txt"
    receipt.write_text("released\n", encoding="utf-8")
    emit_evidence(root, "SHIPME", "release.receipt", receipt, "2026-11-12T00:00:00Z",
                  state_dir=tmp_path)
    with pytest.raises(SddError, match="migration-evidenced"):
        set_phase(root, "SHIPME", "ship", "ready", strict=True,
                  evidence_dir=evidence, state_dir=tmp_path)


def test_migration_gate_skipped_for_critical(tmp_path: Path) -> None:
    """critical profile ships without migration.plan — scope is honest."""
    from apiforge.sdd.evidence import emit_evidence

    root = _ship_feature(tmp_path, "critical")
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    receipt = tmp_path / "receipt.txt"
    receipt.write_text("released\n", encoding="utf-8")
    emit_evidence(root, "SHIPME", "release.receipt", receipt, "2026-11-12T00:00:00Z",
                  state_dir=tmp_path)
    change = set_phase(root, "SHIPME", "ship", "ready", strict=True,
                       evidence_dir=evidence, state_dir=tmp_path)
    assert change.status == "ready"


def test_migration_plan_extractor(tmp_path: Path) -> None:
    """migration.plan evidence extracts rollback/cutover from frontmatter."""
    from apiforge.sdd.evidence import emit_evidence

    root = _ship_feature(tmp_path, "migration")
    plan = tmp_path / "mig.md"
    plan.write_text(
        "---\nrollback: restore-snapshot\ncutover: dns-swap\nrepositories: [a, b]\n---\n# m\n",
        encoding="utf-8",
    )
    payload = emit_evidence(root, "SHIPME", "migration.plan", plan,
                            "2026-11-12T00:00:00Z", state_dir=tmp_path)
    assert payload["extracted"]["rollback"] == "restore-snapshot"
    assert payload["extracted"]["cutover"] == "dns-swap"

    # without rollback/cutover the evidence is refused, not faked
    plan.write_text("---\nrepositories: [a]\n---\n", encoding="utf-8")
    with pytest.raises(SddError, match="AF-SDD-EVIDENCE-EXTRACT"):
        emit_evidence(root, "SHIPME", "migration.plan", plan,
                      "2026-11-12T00:00:00Z", state_dir=tmp_path)
