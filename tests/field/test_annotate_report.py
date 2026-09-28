import json
from pathlib import Path

import pytest

from apiforge.contracts.field import FieldRun
from apiforge.field.annotate import annotate, verify
from apiforge.field.errors import ENUM, RUN_MISSING, FieldError
from apiforge.field.report import build_report, wilson
from apiforge.field.store import save_run
from tests.field.support import OSS, OWN, corpus, task


def _run(task_id: str, **fields: object) -> FieldRun:
    base = {
        "task_id": task_id,
        "scenario": "multi_repo",
        "repo_ref": OSS,
        "phase": "baseline",
        "run_ids": (f"r-{task_id}",),
        "inference_flag": False,
        "started_at": "2026-10-02T10:00:00Z",
        "ended_at": "2026-10-02T10:30:00Z",
        "time_to_solution_ms": 1800000,
        "verifier_verdict": "agree",
    }
    base.update(fields)
    return FieldRun.model_validate(base)


def test_annotate_rejects_values_outside_enum(tmp_path: Path) -> None:
    corpus(tmp_path)
    save_run(tmp_path, _run("T001"))
    with pytest.raises(FieldError) as exc:
        annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="vibes")
    assert exc.value.code == ENUM
    assert exc.value.field == "exit_reason"
    assert "graph_gap" in exc.value.unlock
    with pytest.raises(FieldError) as exc:
        annotate(tmp_path, task_id="T001", phase="later")
    assert exc.value.field == "phase"


def test_annotate_missing_record(tmp_path: Path) -> None:
    corpus(tmp_path)
    with pytest.raises(FieldError) as exc:
        annotate(tmp_path, task_id="T001", phase="baseline", exit_reason="ux_gap")
    assert exc.value.code == RUN_MISSING


def test_verify_never_echoes_human_labels(tmp_path: Path) -> None:
    corpus(tmp_path)
    save_run(tmp_path, _run("T001", exit_reason="graph_gap", task_completed=True))
    out = verify(tmp_path, task_id="T001", phase="baseline", verdict="disagree")
    assert out == {"task_id": "T001", "phase": "baseline", "verifier_verdict": "disagree"}


def test_divergent_run_counts_as_unresolved(tmp_path: Path) -> None:
    corpus(tmp_path)
    save_run(
        tmp_path, _run("T001", task_completed=True, exit_reason="none", verifier_verdict="disagree")
    )
    save_run(tmp_path, _run("T002", task_completed=True, exit_reason="none"))
    report = build_report(tmp_path)
    assert report.unresolved_runs == ("T001",)
    assert report.runs_verified == 1
    assert report.divergence_rate == 0.5


def _seed(root: Path, graph_repos: tuple[str, ...], ux: int) -> None:
    tasks = []
    for index, repo in enumerate(graph_repos):
        tasks.append(task(f"G{index}", repo_ref=repo))
        save_run(root, _run(f"G{index}", repo_ref=repo, exit_reason="graph_gap"))
    for index in range(ux):
        tasks.append(task(f"U{index}"))
        save_run(root, _run(f"U{index}", exit_reason="ux_gap"))
    corpus(root, tasks=tasks)


def test_theme_qualification_needs_two_repos(tmp_path: Path) -> None:
    _seed(tmp_path, (OSS, OSS, OSS, OWN, OWN, OWN), ux=7)
    report = build_report(tmp_path)
    themes = {theme.exit_reason: theme for theme in report.themes}
    assert themes["graph_gap"].qualified and themes["graph_gap"].repos == 2
    assert not themes["ux_gap"].qualified
    assert report.qualified_themes == ("graph_gap",)
    assert report.h1_verdict == "confirmed"
    assert themes["ux_gap"].ci95 == wilson(7, 13)


def test_refuted_when_other_theme_wins(tmp_path: Path) -> None:
    tasks = []
    for index in range(6):
        repo = OSS if index % 2 else OWN
        tasks.append(task(f"K{index}", repo_ref=repo))
        save_run(tmp_path, _run(f"K{index}", repo_ref=repo, exit_reason="knowledge_gap"))
    corpus(tmp_path, tasks=tasks)
    assert build_report(tmp_path).h1_verdict == "refuted"


def test_inconclusive_without_dominant_theme(tmp_path: Path) -> None:
    _seed(tmp_path, (OSS, OSS), ux=3)
    report = build_report(tmp_path)
    assert report.h1_verdict == "inconclusive"
    assert report.qualified_themes == ()
    assert report.recommendation.startswith("inconclusive")
    assert "maintenance" in report.scenarios_under_min
    assert "multi_repo" not in report.scenarios_under_min


def test_report_is_byte_deterministic(tmp_path: Path) -> None:
    _seed(tmp_path, (OSS, OWN, OSS, OWN, OSS), ux=2)
    first = json.dumps(build_report(tmp_path).model_dump(mode="json"), sort_keys=True)
    second = json.dumps(build_report(tmp_path).model_dump(mode="json"), sort_keys=True)
    assert first == second


def test_ab_deltas(tmp_path: Path) -> None:
    corpus(tmp_path, tasks=[task("M1")])
    save_run(tmp_path, _run("M1", manual_context_required=True))
    save_run(
        tmp_path,
        _run(
            "M1",
            phase="ab_on",
            inference_flag=True,
            manual_context_required=False,
            time_to_solution_ms=600000,
        ),
    )
    report = build_report(tmp_path, ab=True)
    assert len(report.ab) == 1
    delta = report.ab[0]
    assert delta.baseline_manual_context is True and delta.ab_manual_context is False
    assert delta.time_delta_ms == -1200000
    assert build_report(tmp_path).ab == ()


def test_wilson_known_values() -> None:
    assert wilson(0, 0) == (0.0, 0.0)
    low, high = wilson(8, 30)
    assert (low, high) == (0.1418, 0.4445)
