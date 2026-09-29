import json
from datetime import timedelta
from pathlib import Path

import pytest
import yaml

from apiforge.contracts.field import SCENARIOS, FieldRun
from apiforge.field.annotate import annotate, verify
from apiforge.field.corpus import load_corpus
from apiforge.field.errors import (
    ACTOR_INVALID,
    CYCLE_EXPIRED,
    CYCLE_MUTATED,
    VERIFIER_NOT_INDEPENDENT,
    FieldError,
)
from apiforge.field.export import export
from apiforge.field.identity import compute_identity, ensure_cycle, lock_path, seal
from apiforge.field.readiness import cycle_state, verification_state
from apiforge.field.record import record
from apiforge.field.report import build_report
from apiforge.field.store import load_run, save_run
from tests.field.support import (
    ENDED,
    EXECUTOR,
    HUMAN,
    NOW,
    OSS,
    OWN,
    STARTED,
    VERIFIER,
    corpus,
    field_run,
    runtime_run,
    task,
    verified,
)

FIELD = Path("docs") / "field"


def _record(root: Path, task_id: str = "T001", **overrides: object) -> FieldRun:
    args: dict[str, object] = {
        "task_id": task_id,
        "run_ids": ("run-1",),
        "phase": "baseline",
        "started_at": STARTED,
        "ended_at": ENDED,
        "executor": EXECUTOR,
        "now": NOW,
    }
    args.update(overrides)
    return record(root, **args)  # type: ignore[arg-type]


def _sealed(root: Path, tasks: list[dict[str, object]] | None = None) -> None:
    corpus(root, tasks=tasks)
    runtime_run(root, "run-1")
    _record(root)


def _edit_corpus(root: Path, mutate) -> None:
    path = root / FIELD / "corpus.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _mutation(root: Path) -> FieldError:
    with pytest.raises(FieldError) as exc:
        build_report(root)
    assert exc.value.code == CYCLE_MUTATED
    assert "sealed commit" in exc.value.unlock
    return exc.value


def test_first_record_seals_cycle(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    assert not lock_path(tmp_path).exists()
    _record(tmp_path)
    lock = json.loads(lock_path(tmp_path).read_text(encoding="utf-8"))
    assert lock["schema"] == "apiforge/field-cycle-identity/v1"
    assert lock["cycle_started_at"] == STARTED
    manifest = load_corpus(tmp_path)
    assert manifest.cycle_started_at == STARTED
    assert compute_identity(tmp_path, manifest, STARTED).corpus_sha256 == lock["corpus_sha256"]
    assert ensure_cycle(tmp_path, manifest) is not None
    _record(tmp_path)
    assert json.loads(lock_path(tmp_path).read_text(encoding="utf-8")) == lock


def test_hypothesis_edit_is_mutation(tmp_path: Path) -> None:
    _sealed(tmp_path)
    (tmp_path / FIELD / "hypothesis.md").write_text("# H1\ncontext_gap dominates\n", "utf-8")
    assert _mutation(tmp_path).field == "cycle.hypothesis_sha256"


def test_backdated_task_is_mutation(tmp_path: Path) -> None:
    _sealed(tmp_path)
    _edit_corpus(
        tmp_path, lambda data: data["tasks"].append(task("T777", at="2026-09-01T00:00:00Z"))
    )
    assert _mutation(tmp_path).field == "cycle.corpus_sha256"


def test_moved_cycle_start_is_mutation(tmp_path: Path) -> None:
    _sealed(tmp_path)
    _edit_corpus(tmp_path, lambda data: data.update(cycle_started_at="2026-12-01T00:00:00Z"))
    assert _mutation(tmp_path).field == "cycle.cycle_started_at"


def test_gate_edit_is_mutation(tmp_path: Path) -> None:
    _sealed(tmp_path)
    _edit_corpus(tmp_path, lambda data: data["gate"].update(max_runs=400))
    assert _mutation(tmp_path).field == "cycle.corpus_sha256"


def test_missing_lock_is_mutation(tmp_path: Path) -> None:
    _sealed(tmp_path)
    lock_path(tmp_path).unlink()
    assert _mutation(tmp_path).field == "cycle.lock"


def test_lock_without_cycle_start_is_mutation(tmp_path: Path) -> None:
    _sealed(tmp_path)
    _edit_corpus(tmp_path, lambda data: data.update(cycle_started_at=None))
    assert _mutation(tmp_path).field == "cycle.cycle_started_at"


def test_mutation_blocks_every_command(tmp_path: Path) -> None:
    _sealed(tmp_path)
    (tmp_path / FIELD / "hypothesis.md").write_text("# changed\n", "utf-8")
    for call in (
        lambda: _record(tmp_path),
        lambda: annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="graph_gap"),
        lambda: verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=HUMAN),
        lambda: export(tmp_path),
    ):
        with pytest.raises(FieldError) as exc:
            call()
        assert exc.value.code == CYCLE_MUTATED


def test_crlf_hypothesis_is_not_mutation(tmp_path: Path) -> None:
    _sealed(tmp_path)
    path = tmp_path / FIELD / "hypothesis.md"
    lf = path.read_bytes().replace(b"\r\n", b"\n")
    for content in (lf, lf.replace(b"\n", b"\r\n")):
        path.write_bytes(content)
        assert build_report(tmp_path).cycle_status == "collecting"


def test_annotate_after_verify_is_stale(tmp_path: Path) -> None:
    _sealed(tmp_path)
    annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="graph_gap")
    verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=HUMAN)
    assert build_report(tmp_path).runs_verified == 1
    annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="context_gap")
    run = load_run(tmp_path, "T001", "baseline")
    assert run.verification is not None and run.verification.verdict == "agree"
    assert verification_state(run) == "stale"
    report = build_report(tmp_path)
    assert report.stale_runs == ("T001",)
    assert report.unresolved_runs == ("T001",)
    assert report.runs_verified == 0
    assert all(theme.count == 0 for theme in report.themes)


def test_rerecord_with_other_runs_is_stale(tmp_path: Path) -> None:
    _sealed(tmp_path)
    verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=HUMAN)
    runtime_run(tmp_path, "run-2")
    _record(tmp_path, run_ids=("run-1", "run-2"))
    assert verification_state(load_run(tmp_path, "T001", "baseline")) == "stale"


def test_reverify_clears_stale(tmp_path: Path) -> None:
    _sealed(tmp_path)
    annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="graph_gap")
    verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=HUMAN)
    annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="context_gap")
    verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=VERIFIER)
    report = build_report(tmp_path)
    assert report.stale_runs == ()
    assert {theme.exit_reason: theme.count for theme in report.themes}["context_gap"] == 1


def test_self_verification_refused(tmp_path: Path) -> None:
    _sealed(tmp_path)
    before = load_run(tmp_path, "T001", "baseline")
    with pytest.raises(FieldError) as exc:
        verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=EXECUTOR)
    assert exc.value.code == VERIFIER_NOT_INDEPENDENT
    assert exc.value.field == "verifier"
    assert load_run(tmp_path, "T001", "baseline") == before


@pytest.mark.parametrize(
    "actor",
    ["human:operator-name", "human:sha256:abc", "robot:x", "agent:Api Verifier", "agent:", ""],
)
def test_invalid_actor_refused(tmp_path: Path, actor: str) -> None:
    _sealed(tmp_path)
    with pytest.raises(FieldError) as exc:
        verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=actor)
    assert exc.value.code == ACTOR_INVALID
    assert "human:sha256" in exc.value.unlock
    with pytest.raises(FieldError) as exc:
        _record(tmp_path, executor=actor)
    assert exc.value.code == ACTOR_INVALID
    assert exc.value.field == "executor"


def _seed_sealed(root: Path, runs: list[FieldRun], started: str = STARTED) -> None:
    tasks = [task(run.task_id, scenario=run.scenario, repo_ref=run.repo_ref) for run in runs]
    corpus(root, tasks=tasks)
    seal(root, load_corpus(root), started)
    for run in runs:
        save_run(root, run)


def _agreed(task_id: str, scenario: str, repo_ref: str = OSS, **fields: object) -> FieldRun:
    return verified(
        field_run(task_id, scenario=scenario, repo_ref=repo_ref, exit_reason="graph_gap", **fields)
    )


def test_early_stop_stays_collecting(tmp_path: Path) -> None:
    runs = [_agreed(f"G{i}", "multi_repo", OSS if i % 2 else OWN) for i in range(5)]
    _seed_sealed(tmp_path, runs)
    report = build_report(tmp_path)
    assert report.qualified_themes == ("graph_gap",)
    assert report.cycle_status == "collecting"
    assert report.provisional_h1 == "confirmed"
    assert report.h1_verdict == "inconclusive"
    assert report.recommendation.startswith("continue collecting")
    assert "open follow-up" not in report.recommendation
    assert report.coverage_gate.enough_scenarios is False
    assert report.coverage_gate.deadline == "2026-10-30T10:00:00Z"


def test_full_coverage_is_ready(tmp_path: Path) -> None:
    runs = [
        _agreed(f"{scenario[:3]}{i}", scenario, OSS if i % 2 else OWN)
        for scenario in SCENARIOS
        for i in range(5)
    ]
    _seed_sealed(tmp_path, runs)
    report = build_report(tmp_path)
    assert report.cycle_status == "ready"
    assert report.h1_verdict == "confirmed" == report.provisional_h1
    assert report.recommendation == "open follow-up SDDs for at most two themes: graph_gap"
    assert report.coverage_gate.within_timebox is True


def test_expired_by_runs(tmp_path: Path) -> None:
    runs = [_agreed(f"M{i:02d}", "multi_repo") for i in range(40)]
    _seed_sealed(tmp_path, runs)
    report = build_report(tmp_path)
    assert report.cycle_status == "expired"
    assert report.h1_verdict == "inconclusive"
    assert report.recommendation == "inconclusive: extend the corpus; open no new feature"
    assert report.coverage_gate.runs_total == 40


def test_expired_by_weeks(tmp_path: Path) -> None:
    runs = [_agreed(f"G{i}", "multi_repo") for i in range(5)]
    _seed_sealed(tmp_path, runs)
    late = NOW + timedelta(weeks=5)
    assert build_report(tmp_path, now=late).cycle_status == "expired"
    assert build_report(tmp_path, now=NOW).cycle_status == "collecting"


def test_record_after_expiry_refused(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    _record(tmp_path)
    with pytest.raises(FieldError) as exc:
        _record(tmp_path, now=NOW + timedelta(weeks=5))
    assert exc.value.code == CYCLE_EXPIRED
    assert exc.value.field == "cycle"


def test_ready_cycle_at_max_runs_refuses_new_baseline(tmp_path: Path) -> None:
    runs = [
        _agreed(f"{scenario[:3]}{i}", scenario, OSS if i % 2 else OWN)
        for scenario in SCENARIOS
        for i in range(5)
    ]
    runs += [_agreed(f"X{i}", "multi_repo") for i in range(10)]
    tasks = [task(run.task_id, scenario=run.scenario, repo_ref=run.repo_ref) for run in runs]
    corpus(tmp_path, tasks=[*tasks, task("T001")])
    seal(tmp_path, load_corpus(tmp_path), "2026-10-01T10:00:00Z")
    for run in runs:
        save_run(tmp_path, run)
    status, coverage = cycle_state(load_corpus(tmp_path), tuple(runs), NOW)
    assert (status, coverage.runs_total) == ("ready", 40)
    runtime_run(tmp_path, "run-1")
    with pytest.raises(FieldError) as exc:
        _record(tmp_path)
    assert exc.value.code == CYCLE_EXPIRED
    assert _record(tmp_path, task_id="X0").task_id == "X0"


def test_export_carries_cycle_status_and_identity(tmp_path: Path) -> None:
    _sealed(tmp_path)
    annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="graph_gap")
    verify(tmp_path, task_id="T001", phase="baseline", verdict="agree", verifier=HUMAN)
    out = export(tmp_path, out_dir=tmp_path / "out")
    assert out["exported"] == 1
    assert out["cycle_status"] == "collecting"
    assert out["cycle_identity"]["cycle_started_at"] == STARTED
    annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="ux_gap")
    assert export(tmp_path, out_dir=tmp_path / "out2")["exported"] == 0
