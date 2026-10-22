"""lf-0038 (install-2.0 §7): classified eval catalog, §7.2 ops, §7.3 security."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.evals import catalog as evals_catalog

ROOT = Path(__file__).resolve().parents[1]


# --- §7.1: classified inventory -------------------------------------------------


def test_catalog_covers_all_four_kinds():
    rows = evals_catalog.catalog()
    kinds = {row["kind"] for row in rows}
    assert kinds == {
        "developer",
        "runtime-decision",
        "output-verification",
        "host-conformance",
    }
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["kind"]] = counts.get(row["kind"], 0) + 1
    assert counts["developer"] >= 10
    assert all(counts[k] >= 3 for k in ("runtime-decision", "output-verification", "host-conformance"))


def test_catalog_is_metadata_only():
    blob = json.dumps(evals_catalog.catalog())
    # sealed corpus content never leaks into agent-facing metadata
    assert "haiku-H001" not in blob
    assert "api-orchestrator" not in blob
    assert '"expected"' not in blob


def test_manifest_suites_validate_as_context_entries():
    from apiforge import _forgecontext as fctx

    entries = evals_catalog.manifest_suites()
    assert {e["kind"] for e in entries} == set(fctx.EVAL_KINDS)
    problems: list[str] = []
    for i, entry in enumerate(entries):
        fctx._eval_suite(entry, problems, f"$.eval_suites[{i}]")
    assert problems == []


def test_context_manifest_carries_classified_evals_and_ops(tmp_path):
    from apiforge import _forgecontext as fctx
    from apiforge import _installkit as kit
    from apiforge.install.service import _context_manifest, _spec

    ctx = kit.InstallContext(
        spec=_spec(),
        scope="project",
        root=tmp_path,
        state_dir=tmp_path / ".apiforge",
        profile="recommended",
        hosts=("claude",),
    )
    manifest = _context_manifest(ctx)
    assert fctx.validate_manifest(manifest) == []
    ops = manifest["discovery"]["ops"]
    for op in (
        "evals.list",
        "evals.describe",
        "evals.run",
        "evals.result",
        "verification.plan",
        "verification.run",
    ):
        assert op in ops, f"missing op {op}"
    declared = {c["id"] for c in manifest["discovery"]["commands"]}
    assert set(ops.values()) <= declared
    kinds = {s["kind"] for s in manifest["eval_suites"]}
    assert kinds == set(fctx.EVAL_KINDS)
    assert manifest["capabilities"]["evals"]["count"] == len(manifest["eval_suites"])


# --- §7.3: security ------------------------------------------------------------


def test_holdout_answers_never_exposed():
    """The agent-routing holdout seals expected agent names; describe exposes
    only path + sha256 + count — the holdout content never appears."""
    holdout = ROOT / "evals" / "corpus" / "agent-routing" / "holdout.json"
    secrets = json.loads(holdout.read_text(encoding="utf-8"))["cases"][0]
    doc = evals_catalog.describe("agent-routing", root=ROOT)
    blob = json.dumps(doc)
    assert secrets["expected"] not in blob
    assert secrets["question"] not in blob
    assert secrets["id"] not in blob
    sealed = doc["sealed"]
    assert sealed["count"] == 1
    entry = sealed["resolved"][0]
    assert entry["sha256"] == hashlib.sha256(holdout.read_bytes()).hexdigest()
    assert sealed["content"].startswith("sealed")


def test_baseline_hash_recorded_and_tamper_evident(tmp_path):
    doc = evals_catalog.describe("economy", root=ROOT)
    baseline = ROOT / "evals" / "corpus" / "economy" / "baseline.json"
    entry = doc["sealed"]["resolved"][0]
    assert entry["sha256"] == hashlib.sha256(baseline.read_bytes()).hexdigest()


def test_describe_unknown_suite_refused():
    with pytest.raises(ContractError) as exc:
        evals_catalog.describe("no-such-suite")
    assert exc.value.code == "AF-EVALS-SUITE-UNKNOWN"


def test_run_missing_inputs_is_a_named_refusal():
    """§7.4: a suite needing inputs refuses with AF-EVALS-RUN-INPUT — never a
    silent skip, and the refusal names the native verb."""
    with pytest.raises(ContractError) as exc:
        evals_catalog.run_suite("gate")
    assert exc.value.code == "AF-EVALS-RUN-INPUT"
    assert "baseline" in exc.value.detail and "candidate" in exc.value.detail
    with pytest.raises(ContractError) as exc2:
        evals_catalog.run_suite("task-verify", options={"task": "t-1"})
    assert exc2.value.code == "AF-EVALS-RUN-INPUT"


def test_run_marks_simulated_vs_deferred_external():
    """Every result carries the environment marker — simulated fixture
    evidence is never real-environment proof; live tiers stay deferred."""
    doc = evals_catalog.run_suite("validate")
    assert doc["environment"] == "simulated"
    live = evals_catalog.describe("live")
    assert live["environment"] == "deferred-external"
    assert "deferred" in live["proof_note"]


def test_result_reads_persisted_report(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(
        json.dumps({"schema": "apiforge/evals-validate/v1", "suite": "validate", "passed": True}),
        encoding="utf-8",
    )
    doc = evals_catalog.result(report)
    assert doc["passed"] is True
    assert doc["suite"] == "validate"
    assert doc["environment"] == "simulated"
    assert len(doc["report_sha256"]) == 64
    with pytest.raises(ContractError) as exc:
        evals_catalog.result(tmp_path / "missing.json")
    assert exc.value.code == "AF-EVALS-RESULT-INVALID"
    bad = tmp_path / "report-list.json"
    bad.write_text("[]", encoding="utf-8")
    with pytest.raises(ContractError) as exc2:
        evals_catalog.result(bad)
    assert exc2.value.code == "AF-EVALS-RESULT-INVALID"
