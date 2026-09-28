"""Anonymized export of verified field tasks into ``evals/corpus/field``."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from apiforge.contracts.field import CorpusManifest
from apiforge.field.corpus import load_corpus, local_repos
from apiforge.field.errors import EXPORT_LEAK, FieldError
from apiforge.field.store import load_runs, write_json

EXPORT_DIR = Path("evals") / "corpus" / "field"
CASE_SCHEMA = "apiforge/field-eval-case/v1"
_PATH_LIKE = re.compile(r"([A-Za-z]:[\\/])|(/home/)|(/Users/)|(\\\\)")


def _leaks(text: str, secrets: tuple[str, ...]) -> list[str]:
    found = [secret for secret in secrets if secret and secret.lower() in text.lower()]
    if _PATH_LIKE.search(text):
        found.append("absolute path")
    return found


def build_cases(root: Path, manifest: CorpusManifest) -> list[dict[str, Any]]:
    tasks = {task.id: task for task in manifest.tasks}
    kinds = {repo.ref: repo.kind for repo in manifest.repos}
    private = local_repos(root)
    secrets = tuple(
        sorted({value for entry in private.values() for value in entry.values() if len(value) >= 3})
    )
    cases: list[dict[str, Any]] = []
    for run in load_runs(root):
        if run.phase != "baseline" or run.verifier_verdict != "agree":
            continue
        task = tasks.get(run.task_id)
        if task is None:
            continue
        if kinds.get(task.repo_ref) == "own" and not task.repo_ref.startswith("sha256:"):
            raise FieldError(
                EXPORT_LEAK,
                f"task {task.id} own repo ref is not hashed",
                field="repo_ref",
                unlock="use sha256:<hex> refs for own repos",
            )
        for field, text in (("prompt", task.prompt), ("ground_truth.ref", task.ground_truth.ref)):
            leaks = _leaks(text, secrets)
            if leaks:
                raise FieldError(
                    EXPORT_LEAK,
                    f"task {task.id} {field} exposes {len(leaks)} private marker(s)",
                    field=field,
                    unlock="rewrite the task text without local names or paths",
                )
        cases.append(
            {
                "schema": CASE_SCHEMA,
                "task_id": task.id,
                "scenario": task.scenario,
                "repo_ref": task.repo_ref,
                "prompt": task.prompt,
                "ground_truth_kind": task.ground_truth.kind,
                "expected": {
                    "task_completed": run.task_completed,
                    "exit_reason": run.exit_reason,
                },
            }
        )
    return cases


def export(root: Path, *, out_dir: Path | None = None) -> dict[str, Any]:
    root = Path(root)
    cases = build_cases(root, load_corpus(root))
    target = Path(out_dir) if out_dir is not None else root / EXPORT_DIR
    written = [
        write_json(target / f"{case['task_id']}.json", case).name
        for case in sorted(cases, key=lambda item: str(item["task_id"]))
    ]
    return {"exported": len(written), "files": written, "directory": EXPORT_DIR.as_posix()}


__all__ = ["CASE_SCHEMA", "EXPORT_DIR", "build_cases", "export"]
