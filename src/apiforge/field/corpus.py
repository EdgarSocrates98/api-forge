"""Pre-registered corpus: tasks must exist before the cycle starts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from apiforge.contracts.field import CorpusManifest, CorpusTask
from apiforge.field.errors import (
    CORPUS_INVALID,
    LATE_REGISTRATION,
    TASK_UNREGISTERED,
    FieldError,
)
from apiforge.field.store import field_dir, parse_ts

CORPUS_NAME = "corpus.yaml"
HYPOTHESIS_NAME = "hypothesis.md"
LOCAL_REPOS_NAME = "repos.local.yaml"


def corpus_path(root: Path) -> Path:
    return field_dir(root) / CORPUS_NAME


def _raw(root: Path) -> dict[str, Any]:
    path = corpus_path(root)
    if not path.is_file():
        raise FieldError(
            CORPUS_INVALID,
            f"{path} is missing",
            field="corpus",
            unlock="create docs/field/corpus.yaml with pre-registered tasks",
        )
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise FieldError(
            CORPUS_INVALID, f"{path}: {exc}", field="corpus", unlock="fix the YAML syntax"
        ) from exc
    if not isinstance(data, dict):
        raise FieldError(
            CORPUS_INVALID, f"{path} is not a mapping", field="corpus", unlock="use a YAML mapping"
        )
    return data


def load_corpus(root: Path) -> CorpusManifest:
    data = _raw(root)
    try:
        manifest = CorpusManifest.model_validate(data)
    except ValidationError as exc:
        raise FieldError(
            CORPUS_INVALID,
            str(exc).splitlines()[0],
            field="corpus",
            unlock="match the apiforge/field-corpus/v1 schema in docs/field/README.md",
        ) from exc
    if not (field_dir(root) / HYPOTHESIS_NAME).is_file():
        raise FieldError(
            CORPUS_INVALID,
            "docs/field/hypothesis.md is missing",
            field="hypothesis",
            unlock="pre-register the hypothesis before recording runs",
        )
    repo_refs = {repo.ref for repo in manifest.repos}
    ids = [task.id for task in manifest.tasks]
    if len(ids) != len(set(ids)):
        raise FieldError(
            CORPUS_INVALID, "duplicate task id", field="tasks", unlock="make task ids unique"
        )
    for task in manifest.tasks:
        if task.repo_ref not in repo_refs:
            raise FieldError(
                CORPUS_INVALID,
                f"task {task.id} references unknown repo {task.repo_ref}",
                field="tasks.repo_ref",
                unlock="declare the repo under `repos` first",
            )
        parse_ts(task.registered_at, field="tasks.registered_at")
    for repo in manifest.repos:
        if repo.kind == "own" and not repo.ref.startswith("sha256:"):
            raise FieldError(
                CORPUS_INVALID,
                f"own repo ref {repo.ref} is not anonymized",
                field="repos.ref",
                unlock="use sha256:<hex> and map it in docs/field/repos.local.yaml",
            )
    return manifest


def registered_task(manifest: CorpusManifest, task_id: str, *, started_at: str) -> CorpusTask:
    task = next((item for item in manifest.tasks if item.id == task_id), None)
    if task is None:
        raise FieldError(
            TASK_UNREGISTERED,
            f"task {task_id} is not in docs/field/corpus.yaml",
            field="task",
            unlock="register the task in corpus.yaml before the cycle starts",
        )
    cutoff = manifest.cycle_started_at or started_at
    if parse_ts(task.registered_at, field="tasks.registered_at") > parse_ts(
        cutoff, field="cycle_started_at"
    ):
        raise FieldError(
            LATE_REGISTRATION,
            f"task {task_id} registered at {task.registered_at}, after cycle start {cutoff}",
            field="task",
            unlock="late tasks cannot join this cycle; register them for the next cycle",
        )
    return task


def mark_cycle_started(root: Path, started_at: str) -> None:
    data = _raw(root)
    if data.get("cycle_started_at"):
        return
    data["cycle_started_at"] = started_at
    corpus_path(root).write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n"
    )


def local_repos(root: Path) -> dict[str, dict[str, str]]:
    path = field_dir(root) / LOCAL_REPOS_NAME
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        return {}
    return {
        str(ref): {str(key): str(value) for key, value in (entry or {}).items()}
        for ref, entry in data.items()
        if isinstance(entry, dict) or entry is None
    }


__all__ = [
    "corpus_path",
    "load_corpus",
    "local_repos",
    "mark_cycle_started",
    "registered_task",
]
