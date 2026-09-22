"""Task persistence: ``<root>/.apiforge/tasks/<id>/`` — spec + revisions + history.

Layout::

    tasks/<id>/task.yaml          TaskSpec (current revision)
    tasks/<id>/revisions/<n>.json TaskRevision (immutable, optionally sealed)
    tasks/<id>/history.jsonl      append-only transition log
    tasks/<id>/runs/<n>.json      run records (steps, hashes, budget use)
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

from apiforge.contracts.agentic import AgenticRun
from apiforge.contracts.base import ContractError
from apiforge.contracts.task import TaskRevision, TaskSpec

_TASK_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def tasks_root(root: Path) -> Path:
    return Path(root) / ".apiforge" / "tasks"


def task_dir(root: Path, task_id: str) -> Path:
    return tasks_root(root) / task_id


def _valid_id(task_id: str) -> None:
    if not _TASK_ID.match(task_id):
        raise ContractError(
            "AF-TASK-ID",
            f"task id {task_id!r} must match {_TASK_ID.pattern}",
        )


def create(root: Path, spec: TaskSpec) -> TaskSpec:
    """Persist a new draft task; an existing id is refused."""
    _valid_id(spec.id)
    directory = task_dir(root, spec.id)
    if directory.exists():
        raise ContractError("AF-TASK-EXISTS", f"task {spec.id!r} already exists")
    (directory / "revisions").mkdir(parents=True)
    (directory / "runs").mkdir(parents=True)
    write_spec(directory, spec)
    _append_history(directory, {"event": "created", "revision": 0})
    return spec


def write_spec(directory: Path, spec: TaskSpec) -> None:
    payload = spec.model_dump(mode="json")
    (directory / "task.yaml").write_text(
        yaml.safe_dump(payload, sort_keys=True, allow_unicode=True),
        encoding="utf-8",
    )


def load(root: Path, task_id: str) -> TaskSpec:
    directory = task_dir(root, task_id)
    path = directory / "task.yaml"
    if not path.is_file():
        raise ContractError("AF-TASK-NOT-FOUND", f"no task {task_id!r} under {root}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return TaskSpec.model_validate(data)


def history(root: Path, task_id: str) -> list[dict[str, object]]:
    path = task_dir(root, task_id) / "history.jsonl"
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _append_history(directory: Path, entry: dict[str, object]) -> None:
    with (directory / "history.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def save_revision(root: Path, spec: TaskSpec, changed_fields: tuple[str, ...]) -> TaskRevision:
    """Write a new revision snapshot; returns the recorded revision."""
    directory = task_dir(root, spec.id)
    content = yaml.safe_dump(spec.model_dump(mode="json"), sort_keys=True)
    revision = TaskRevision(
        task_id=spec.id,
        revision=spec.revision,
        content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        changed_fields=changed_fields,
    )
    (directory / "revisions" / f"{spec.revision}.json").write_text(
        json.dumps(revision.model_dump(mode="json"), sort_keys=True, indent=2),
        encoding="utf-8",
    )
    write_spec(directory, spec)
    return revision


def save_seal(root: Path, revision: TaskRevision) -> None:
    """Rewrite a revision file with its seal — revisions stay immutable after."""
    directory = task_dir(root, revision.task_id)
    path = directory / "revisions" / f"{revision.revision}.json"
    if not path.is_file():
        raise ContractError(
            "AF-TASK-REVISION-MISSING",
            f"no revision {revision.revision} for {revision.task_id!r}",
        )
    path.write_text(
        json.dumps(revision.model_dump(mode="json"), sort_keys=True, indent=2),
        encoding="utf-8",
    )


def record_event(root: Path, task_id: str, event: dict[str, object]) -> None:
    _append_history(task_dir(root, task_id), event)


def record_run(root: Path, task_id: str, run: dict[str, object]) -> Path:
    directory = task_dir(root, task_id)
    runs = directory / "runs"
    runs.mkdir(exist_ok=True)
    index = len(list(runs.glob("*.json")))
    path = runs / f"{index}.json"
    path.write_text(
        json.dumps(run, sort_keys=True, indent=2), encoding="utf-8"
    )
    return path


def record_agentic_run(root: Path, run: AgenticRun) -> Path:
    """Persist a typed agentic run in the TaskSpec run index."""
    return record_run(root, run.task_id, run.model_dump(mode="json"))


def latest_run(root: Path, task_id: str) -> dict[str, object] | None:
    """Return the newest indexed run without interpreting its lifecycle."""
    paths = sorted((task_dir(root, task_id) / "runs").glob("*.json"))
    if not paths:
        return None
    payload = json.loads(paths[-1].read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None
