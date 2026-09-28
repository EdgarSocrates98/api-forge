"""Project existing run artifacts into a field-run record; never collects new telemetry.

Automatic values come only from ``.apiforge/economy.jsonl`` attribution rows,
``summary.json`` and ``economy_checkpoint.json`` of the linked runs. A missing
source leaves the value ``null`` with an ``unresolved`` reason. Inference use is
read from ``workspace.infer`` ledger rows, never from operator input.
"""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from apiforge.contracts.field import FieldPhase, FieldRun
from apiforge.economy.ledger import ledger_path
from apiforge.field.corpus import load_corpus, mark_cycle_started, registered_task
from apiforge.field.errors import FLAG_CONTAMINATION, RUN_MISSING, TIME_ORDER, FieldError
from apiforge.field.store import maybe_load_run, parse_ts, save_run
from apiforge.taskspec.store import tasks_root

INFER_VERB = "workspace.infer"
WINDOW_TOLERANCE = timedelta(seconds=60)
HUMAN_FIELDS = (
    "task_completed",
    "exit_reason",
    "manual_context_required",
    "human_intervention",
    "false_positives",
    "false_negatives",
    "verifier_verdict",
)


def _ledger_rows(root: Path, run_ids: set[str]) -> tuple[bool, list[dict[str, Any]]]:
    path = ledger_path(root)
    if not path.is_file():
        return False, []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("run_id") in run_ids:
            rows.append(row)
    return True, rows


def _run_dir(root: Path, run_id: str) -> Path | None:
    matches = sorted(tasks_root(root).glob(f"*/runs/{run_id.replace(':', '-')}"))
    return matches[0] if matches else None


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def record(
    root: Path,
    *,
    task_id: str,
    run_ids: tuple[str, ...],
    phase: FieldPhase,
    started_at: str,
    ended_at: str,
) -> FieldRun:
    root = Path(root)
    manifest = load_corpus(root)
    task = registered_task(manifest, task_id, started_at=started_at)
    started = parse_ts(started_at, field="started_at")
    ended = parse_ts(ended_at, field="ended_at")
    if ended < started:
        raise FieldError(
            TIME_ORDER,
            f"ended_at {ended_at} precedes started_at {started_at}",
            field="ended_at",
            unlock="pass --ended at or after --started",
        )
    if not run_ids:
        raise FieldError(
            RUN_MISSING, "no run id given", field="run", unlock="pass at least one --run"
        )

    unresolved: list[str] = []
    sources: list[str] = []
    ledger_exists, rows = _ledger_rows(root, set(run_ids))
    if ledger_exists:
        sources.append(_rel(root, ledger_path(root)))
    else:
        unresolved.append("ledger_missing")

    inference_flag = any(row.get("verb") == INFER_VERB for row in rows)
    if phase == "baseline" and inference_flag:
        raise FieldError(
            FLAG_CONTAMINATION,
            f"linked runs used `{INFER_VERB}` during a baseline task",
            field="phase",
            unlock="re-run the task without `workspace graph --infer`, or record it as ab_on",
        )
    if phase == "ab_on" and not inference_flag:
        unresolved.append("ab_on_without_inference")

    attribution = [row for row in rows if isinstance(row.get("cost"), dict)]
    context_bytes: int | None = None
    cache_reuse: int | None = None
    if attribution:
        context_bytes = sum(int(row["cost"].get("context_bytes", 0)) for row in attribution)
        cache_reuse = sum(int(row["cost"].get("cache_hits", 0)) for row in attribution)
    elif ledger_exists:
        unresolved.append("ledger_rows_missing")

    calls: list[int] = []
    checkpoints: list[str] = []
    for run_id in sorted(run_ids):
        directory = _run_dir(root, run_id)
        if directory is None:
            if not any(row.get("run_id") == run_id for row in rows):
                raise FieldError(
                    RUN_MISSING,
                    f"run {run_id} has neither a run directory nor ledger rows",
                    field="run",
                    unlock="pass a run_id printed by the runtime or `context capsule`",
                )
            unresolved.append(f"run_dir_missing:{run_id}")
            continue
        summary = _read_json(directory / "summary.json")
        if summary is None:
            unresolved.append(f"summary_missing:{run_id}")
        else:
            sources.append(_rel(root, directory / "summary.json"))
            for key, values in sorted((summary.get("unresolved") or {}).items()):
                for value in values or ():
                    unresolved.append(f"summary:{key}:{value}")
        checkpoint = _read_json(directory / "economy_checkpoint.json")
        if checkpoint is None:
            unresolved.append(f"checkpoint_missing:{run_id}")
            continue
        sources.append(_rel(root, directory / "economy_checkpoint.json"))
        calls.append(int(checkpoint.get("calls_used", 0)))
        updated = checkpoint.get("updated_at")
        if isinstance(updated, str):
            moment = parse_ts(updated, field="checkpoint.updated_at")
            if not started - WINDOW_TOLERANCE <= moment <= ended + WINDOW_TOLERANCE:
                raise FieldError(
                    TIME_ORDER,
                    f"run {run_id} checkpoint at {updated} lies outside [{started_at}, {ended_at}]",
                    field="started_at",
                    unlock="check --started/--ended; they must bracket every linked run",
                )
            checkpoints.append(updated)

    provider_calls = sum(calls) if calls and len(calls) == len(run_ids) else None
    if calls and provider_calls is None:
        unresolved.append("provider_calls_partial")
    time_to_evidence_ms: int | None = None
    if checkpoints:
        first = min(parse_ts(item, field="checkpoint.updated_at") for item in checkpoints)
        time_to_evidence_ms = max(0, int((first - started).total_seconds() * 1000))
    else:
        unresolved.append("evidence_timestamp_missing")

    previous = maybe_load_run(root, task_id, phase)
    carried = (
        {name: getattr(previous, name) for name in HUMAN_FIELDS} if previous is not None else {}
    )
    run = FieldRun(
        task_id=task.id,
        scenario=task.scenario,
        repo_ref=task.repo_ref,
        phase=phase,
        run_ids=tuple(sorted(run_ids)),
        inference_flag=inference_flag,
        started_at=started_at,
        ended_at=ended_at,
        provider_calls=provider_calls,
        context_bytes=context_bytes,
        cache_reuse=cache_reuse,
        time_to_evidence_ms=time_to_evidence_ms,
        time_to_solution_ms=int((ended - started).total_seconds() * 1000),
        sources=tuple(sorted(set(sources))),
        unresolved=tuple(sorted(set(unresolved))),
        **carried,
    )
    mark_cycle_started(root, started_at)
    save_run(root, run)
    return run


__all__ = ["INFER_VERB", "record"]
