import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.contracts.base import ContractError
from apiforge.economy.phase_budget import plan_phase_budgets
from apiforge.evals.freshness_resume import run_freshness_resume
from apiforge.evidence.live_gate import gate
from apiforge.knowledge.watch import watch_packs
from apiforge.runtime.adapters import FakeModelAdapter
from apiforge.runtime.economy_checkpoint import CHECKPOINT_FILE
from apiforge.runtime.runner import resume_runtime, run_runtime
from apiforge.verification.progressive import escalate
from tests.runtime.economy_support import TASK_ID, economy_task

CORPUS = Path(__file__).resolve().parents[2] / "evals" / "corpus" / "economy-freshness"
NOW = "2026-09-28T00:00:00+00:00"
runner = CliRunner()


def test_watch_flags_only_stale_packs_and_never_fetches() -> None:
    result = watch_packs(CORPUS / "manifest.json", now=NOW, root=CORPUS / "packs")
    states = {entry.pack_id: entry for entry in result.entries}
    assert result.fetches is False
    assert states["fresh-pack"].state == "fresh"
    assert "fingerprint" in " ".join(states["fingerprint-changed"].reasons)
    assert "expired" in " ".join(states["expired-pack"].reasons)
    assert states["no-metadata"].state == "unknown"
    assert states["no-upstream-entry"].state == "unresolved"
    assert set(result.refresh_needed) == {
        "fingerprint-changed",
        "version-changed",
        "expired-pack",
        "window-exceeded",
    }


def test_watch_refuses_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(ContractError) as err:
        watch_packs(tmp_path / "nope.json", now=NOW, root=CORPUS / "packs")
    assert err.value.code == "AF-KNOW-WATCH-MANIFEST"
    assert err.value.unlock  # type: ignore[attr-defined]


def test_gate_keeps_static_questions_local_and_refuses_mutation() -> None:
    static = gate("o campo foi removido?", requested="live_read_only")
    assert (static.mode, static.live_allowed) == ("static", False)
    runtime = gate("isso causou erros em produção?")
    assert (runtime.mode, runtime.live_allowed, runtime.requires_receipt) == (
        "live_read_only",
        True,
        True,
    )
    assert gate("did it cause 5xx in production?", offline=True).mode == "fixture"
    with pytest.raises(ContractError) as err:
        gate("fix it", requested="live_mutation")
    assert err.value.code == "AF-EVIDENCE-MUTATION-REFUSED"
    assert err.value.field == "mode"  # type: ignore[attr-defined]


def test_escalation_stops_on_test_and_never_goes_past_read_only() -> None:
    assert escalate(static="likely", test="failed").action == "stop"
    assert escalate(static="likely").next_mode == "test"
    inconclusive = escalate(static="likely", test="inconclusive")
    assert (inconclusive.action, inconclusive.next_mode) == ("escalate", "live_read_only")
    exhausted = escalate(static="likely", test="inconclusive", runtime="inconclusive")
    assert exhausted.action == "unresolved"
    assert exhausted.unresolved[0].startswith("AF-VERIFY-ESCALATE-EXHAUSTED")


def test_escalation_reads_a_test_slice(tmp_path: Path) -> None:
    empty = {
        "schema": "apiforge/test-slice/v1",
        "format": "pytest",
        "log_ref": "ctx://sha256/abc",
        "original_bytes": 10,
    }
    path = tmp_path / "slice.json"
    path.write_text(json.dumps(empty), encoding="utf-8")
    assert escalate(test_slice=path).action == "escalate"
    path.write_text(json.dumps({**empty, "passed": 3}), encoding="utf-8")
    assert escalate(test_slice=path).action == "stop"


def test_phase_budgets_sum_to_envelope_and_protect_safety_phases() -> None:
    plan = plan_phase_budgets("economy")
    assert sum(row.calls for row in plan.phases) == plan.total_calls
    assert all(row.calls >= 1 for row in plan.phases if row.protected)
    over = plan_phase_budgets("economy", usage={"build": {"calls": 9}, "verify": {"calls": 9}})
    statuses = {row.phase: row.status for row in over.phases}
    assert statuses["build"] == "exceeded"
    assert statuses["verify"] == "protected_overrun"
    assert over.status == "unresolved"
    with pytest.raises(ContractError) as err:
        plan_phase_budgets("economy", usage={"deploy": {"calls": 1}})
    assert err.value.code == "AF-BUDGET-PHASE-UNKNOWN"


def test_resume_pins_checkpoint_profile_and_carries_spend(tmp_path: Path) -> None:
    economy_task(tmp_path)
    first = run_runtime(
        tmp_path,
        TASK_ID,
        adapter=FakeModelAdapter({"task-review": {"__error__": "transient"}}),
        now="2026-09-28T10:00:00+00:00",
        profile="deep",
    )
    run_dir = Path(str(first["run_dir"]))
    checkpoint = json.loads((run_dir / CHECKPOINT_FILE).read_text(encoding="utf-8"))
    assert checkpoint["effective"] == "deep"
    resumed = resume_runtime(tmp_path, TASK_ID, profile="economy")
    economy = resumed["economy"]
    assert economy["checkpoint"]["effective"] == "deep"
    assert economy["checkpoint"]["resumes"] == 1
    assert economy["checkpoint"]["calls_used"] >= checkpoint["calls_used"]
    assert any(note.startswith("AF-ECONOMY-RESUME-PINNED") for note in economy["diagnostics"])
    shown = runner.invoke(
        app, ["runtime", "checkpoint", TASK_ID, str(checkpoint["run_id"]), "--root", str(tmp_path)]
    )
    assert shown.exit_code == 0, shown.output
    assert json.loads(shown.output)["resumes"] == 1


def test_eval_corpus_passes() -> None:
    result = run_freshness_resume(CORPUS)
    assert result["passed"], result
    assert result["cases"] >= 16
