from pathlib import Path

import pytest
import yaml

from apiforge.field.corpus import load_corpus
from apiforge.field.errors import (
    CORPUS_INVALID,
    FLAG_CONTAMINATION,
    LATE_REGISTRATION,
    RUN_MISSING,
    TASK_UNREGISTERED,
    TIME_ORDER,
    FieldError,
)
from apiforge.field.identity import seal
from apiforge.field.record import record
from tests.field.support import ENDED, EXECUTOR, NOW, STARTED, corpus, runtime_run, task


def _record(root: Path, **overrides: object):
    args = {
        "task_id": "T001",
        "run_ids": ("run-1",),
        "phase": "baseline",
        "started_at": STARTED,
        "ended_at": ENDED,
        "executor": EXECUTOR,
        "now": NOW,
    }
    args.update(overrides)
    return record(root, **args)  # type: ignore[arg-type]


def test_record_joins_existing_artifacts(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    run = _record(tmp_path)
    assert run.provider_calls == 3
    assert run.context_bytes == 1200
    assert run.cache_reuse == 2
    assert run.time_to_solution_ms == 30 * 60 * 1000
    assert run.time_to_evidence_ms == 5 * 60 * 1000
    assert run.inference_flag is False
    assert "summary:routing:no-route" in run.unresolved
    assert any(source.endswith("economy_checkpoint.json") for source in run.sources)
    assert (tmp_path / "docs" / "field" / "runs" / "T001__baseline.json").is_file()
    saved = yaml.safe_load((tmp_path / "docs" / "field" / "corpus.yaml").read_text())
    assert saved["cycle_started_at"] == STARTED
    assert run.executor.kind == "agent" and run.executor.id == "api-orchestrator"


def test_unregistered_task_is_refused(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    with pytest.raises(FieldError) as exc:
        _record(tmp_path, task_id="T999")
    assert exc.value.code == TASK_UNREGISTERED
    assert exc.value.field == "task"
    assert "corpus" in exc.value.unlock


def test_late_registration_is_refused(tmp_path: Path) -> None:
    corpus(tmp_path, tasks=[task("T001"), task("T002", at="2026-10-03T00:00:00Z")])
    seal(tmp_path, load_corpus(tmp_path), "2026-10-02T09:00:00Z")
    runtime_run(tmp_path, "run-1", updated_at="2026-10-04T10:05:00Z")
    with pytest.raises(FieldError) as exc:
        _record(
            tmp_path,
            task_id="T002",
            started_at="2026-10-04T10:00:00Z",
            ended_at="2026-10-04T10:30:00Z",
        )
    assert exc.value.code == LATE_REGISTRATION


def test_baseline_with_inference_is_contaminated(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1", verbs=("context.capsule", "workspace.infer"))
    with pytest.raises(FieldError) as exc:
        _record(tmp_path)
    assert exc.value.code == FLAG_CONTAMINATION
    assert not (tmp_path / "docs" / "field" / "runs" / "T001__baseline.json").exists()


def test_ab_on_derives_flag_from_ledger(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1", verbs=("workspace.infer",))
    run = _record(tmp_path, phase="ab_on")
    assert run.inference_flag is True
    assert "ab_on_without_inference" not in run.unresolved


def test_missing_ledger_leaves_honest_nulls(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1", ledger=False, checkpoint=False)
    run = _record(tmp_path)
    assert run.context_bytes is None and run.cache_reuse is None
    assert run.provider_calls is None and run.time_to_evidence_ms is None
    assert {"ledger_missing", "checkpoint_missing:run-1", "evidence_timestamp_missing"} <= set(
        run.unresolved
    )


def test_unknown_run_is_refused(tmp_path: Path) -> None:
    corpus(tmp_path)
    with pytest.raises(FieldError) as exc:
        _record(tmp_path, run_ids=("ghost",))
    assert exc.value.code == RUN_MISSING


def test_time_order_and_window(tmp_path: Path) -> None:
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    with pytest.raises(FieldError) as exc:
        _record(tmp_path, ended_at="2026-10-02T09:00:00Z")
    assert exc.value.code == TIME_ORDER
    runtime_run(tmp_path, "run-2", updated_at="2026-10-02T12:00:00Z")
    with pytest.raises(FieldError) as exc:
        _record(tmp_path, run_ids=("run-2",))
    assert exc.value.code == TIME_ORDER


def test_rerecord_keeps_human_labels(tmp_path: Path) -> None:
    from apiforge.field.annotate import annotate

    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    _record(tmp_path)
    annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="graph_gap")
    assert _record(tmp_path).exit_reason == "graph_gap"


def test_corpus_rejects_unhashed_own_repo(tmp_path: Path) -> None:
    corpus(tmp_path, repos=[{"ref": "my-private-repo", "kind": "own"}], tasks=[])
    with pytest.raises(FieldError) as exc:
        _record(tmp_path)
    assert exc.value.code == CORPUS_INVALID
    assert exc.value.field == "repos.ref"


def test_missing_hypothesis_is_refused(tmp_path: Path) -> None:
    corpus(tmp_path)
    (tmp_path / "docs" / "field" / "hypothesis.md").unlink()
    with pytest.raises(FieldError) as exc:
        _record(tmp_path)
    assert exc.value.code == CORPUS_INVALID
    assert exc.value.field == "hypothesis"


def test_repository_corpus_template_validates() -> None:
    from apiforge.field.corpus import load_corpus

    manifest = load_corpus(Path(__file__).resolve().parents[2])
    assert manifest.cycle_started_at is None
    assert manifest.hypothesis.category == "graph_gap"
