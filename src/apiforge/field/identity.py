"""Sealed field-cycle identity: pre-registration as an invariant, not a convention.

The first ``field record`` writes ``docs/field/cycle.lock.json``; every field
command recomputes the identity from ``corpus.yaml`` and ``hypothesis.md`` and
refuses when a sealed component differs or the lock is missing.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from apiforge.contracts.field import CorpusManifest, FieldCycleIdentity
from apiforge.field.corpus import HYPOTHESIS_NAME, mark_cycle_started
from apiforge.field.errors import CYCLE_MUTATED, FieldError
from apiforge.field.store import field_dir, write_json

LOCK_NAME = "cycle.lock.json"
_UNLOCK = "restore docs/field to the sealed commit, or start a new cycle with a new corpus"


def lock_path(root: Path) -> Path:
    return field_dir(root) / LOCK_NAME


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _hypothesis_sha(root: Path) -> str:
    text = (field_dir(root) / HYPOTHESIS_NAME).read_bytes().decode("utf-8")
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def git_head(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    head = out.stdout.strip()
    return head if out.returncode == 0 and len(head) == 40 else None


def compute_identity(
    root: Path, manifest: CorpusManifest, started_at: str, *, git_commit: str | None = None
) -> FieldCycleIdentity:
    body = manifest.model_dump(mode="json")
    body.pop("cycle_started_at", None)
    return FieldCycleIdentity(
        cycle_started_at=started_at,
        corpus_sha256=sha256_json(body),
        hypothesis_sha256=_hypothesis_sha(root),
        gate_sha256=sha256_json(body["gate"]),
        tasks_sha256=sha256_json(sorted(body["tasks"], key=lambda item: item["id"])),
        repos_sha256=sha256_json(sorted(body["repos"], key=lambda item: item["ref"])),
        git_commit=git_commit,
    )


def _mutated(component: str, detail: str) -> FieldError:
    return FieldError(CYCLE_MUTATED, detail, field=f"cycle.{component}", unlock=_UNLOCK)


def read_lock(root: Path) -> FieldCycleIdentity | None:
    path = lock_path(root)
    if not path.is_file():
        return None
    try:
        return FieldCycleIdentity.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (ValueError, ValidationError) as exc:
        raise _mutated("lock", f"{path.name} is not a valid field-cycle identity") from exc


def ensure_cycle(root: Path, manifest: CorpusManifest) -> FieldCycleIdentity | None:
    sealed = read_lock(root)
    if manifest.cycle_started_at is None:
        if sealed is not None:
            raise _mutated("cycle_started_at", "lock exists but corpus cycle_started_at is null")
        return None
    if sealed is None:
        raise _mutated("lock", f"cycle started at {manifest.cycle_started_at} but lock is missing")
    current = compute_identity(root, manifest, manifest.cycle_started_at)
    difference = sealed.first_difference(current)
    if difference is not None:
        raise _mutated(difference, f"{difference} differs from the sealed cycle")
    return sealed


def seal(root: Path, manifest: CorpusManifest, started_at: str) -> FieldCycleIdentity:
    mark_cycle_started(root, started_at)
    identity = compute_identity(root, manifest, started_at, git_commit=git_head(root))
    write_json(lock_path(root), identity.model_dump(mode="json"))
    return identity


__all__ = [
    "LOCK_NAME",
    "compute_identity",
    "ensure_cycle",
    "git_head",
    "lock_path",
    "read_lock",
    "seal",
    "sha256_json",
]
