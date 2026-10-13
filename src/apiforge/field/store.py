"""Deterministic persistence of field-run records under ``docs/field/runs``."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from apiforge.contracts.field import FieldRun
from apiforge.field.errors import RUN_MISSING, TIME_ORDER, FieldError

FIELD_DIR = Path("docs") / "field"


def field_dir(root: Path) -> Path:
    return Path(root) / FIELD_DIR


def runs_dir(root: Path) -> Path:
    return field_dir(root) / "runs"


def run_path(root: Path, task_id: str, phase: str) -> Path:
    return runs_dir(root) / f"{task_id}__{phase}.json"


def parse_ts(value: str, *, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise FieldError(
            TIME_ORDER,
            f"{value!r} is not RFC3339",
            field=field,
            unlock="pass an RFC3339 timestamp such as 2026-10-01T12:00:00Z",
        ) from exc
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    temporary.replace(path)
    return path


def save_run(root: Path, run: FieldRun) -> Path:
    return write_json(run_path(root, run.task_id, run.phase), run.model_dump(mode="json"))


def load_run(root: Path, task_id: str, phase: str) -> FieldRun:
    path = run_path(root, task_id, phase)
    if not path.is_file():
        raise FieldError(
            RUN_MISSING,
            f"no field record for task {task_id} phase {phase}",
            field="task",
            unlock="run `apiforge field record` for this task and phase first",
        )
    return FieldRun.model_validate(json.loads(path.read_text(encoding="utf-8")))


def maybe_load_run(root: Path, task_id: str, phase: str) -> FieldRun | None:
    path = run_path(root, task_id, phase)
    if not path.is_file():
        return None
    return FieldRun.model_validate(json.loads(path.read_text(encoding="utf-8")))


def load_runs(root: Path) -> tuple[FieldRun, ...]:
    directory = runs_dir(root)
    if not directory.is_dir():
        return ()
    return tuple(
        FieldRun.model_validate(json.loads(path.read_text(encoding="utf-8")))
        for path in sorted(directory.glob("*.json"))
    )


__all__ = [
    "field_dir",
    "load_run",
    "load_runs",
    "maybe_load_run",
    "parse_ts",
    "run_path",
    "runs_dir",
    "save_run",
    "write_json",
]
