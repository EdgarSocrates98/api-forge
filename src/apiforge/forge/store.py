"""Forge task persistence: ``<root>/.apiforge/forge/`` — append-only, JSON only.

Layout::

    forge/tasks/<task_id>/request.json   ForgeTaskRequest (immutable)
    forge/tasks/<task_id>/status.json    ForgeTaskStatus (last persisted)
    forge/tasks/<task_id>/events.jsonl   append-only transitions
    forge/handoffs/<handoff_id>.json     ForgeHandoff bundles
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.forge_protocol import (
    ForgeHandoff,
    ForgeTaskRequest,
    ForgeTaskStatus,
)

_TASK_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def forge_root(root: Path) -> Path:
    return Path(root) / ".apiforge" / "forge"


def task_dir(root: Path, task_id: str) -> Path:
    return forge_root(root) / "tasks" / task_id


def _valid_id(task_id: str) -> None:
    if not _TASK_ID.match(task_id):
        raise ContractError(
            "AF-FORGE-TASK-ID",
            f"task id {task_id!r} must match {_TASK_ID.pattern}",
        )


def create_task(root: Path, request: ForgeTaskRequest, status: ForgeTaskStatus) -> None:
    """Persist a new forge task; an existing id is refused."""
    _valid_id(request.task_id)
    directory = task_dir(root, request.task_id)
    if directory.exists():
        raise ContractError(
            "AF-FORGE-TASK-EXISTS", f"forge task {request.task_id!r} already exists"
        )
    directory.mkdir(parents=True)
    (directory / "request.json").write_text(request.model_dump_json(indent=2), encoding="utf-8")
    write_status(directory, status)
    append_event(directory, {"event": "received", "state": "received", "at": status.updated_at})
    append_event(directory, {"event": "accepted", "state": status.state, "at": status.updated_at})


def write_status(directory: Path, status: ForgeTaskStatus) -> None:
    (directory / "status.json").write_text(status.model_dump_json(indent=2), encoding="utf-8")


def append_event(directory: Path, entry: dict[str, object]) -> None:
    with (directory / "events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def load_request(root: Path, task_id: str) -> ForgeTaskRequest:
    path = task_dir(root, task_id) / "request.json"
    if not path.is_file():
        raise ContractError("AF-FORGE-TASK-NOT-FOUND", f"no forge task {task_id!r} under {root}")
    try:
        return ForgeTaskRequest.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise ContractError("AF-FORGE-STORE", f"{path}: {exc}") from exc


def load_status(root: Path, task_id: str) -> ForgeTaskStatus:
    path = task_dir(root, task_id) / "status.json"
    if not path.is_file():
        raise ContractError("AF-FORGE-TASK-NOT-FOUND", f"no forge task {task_id!r} under {root}")
    try:
        return ForgeTaskStatus.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise ContractError("AF-FORGE-STORE", f"{path}: {exc}") from exc


def task_ids(root: Path) -> list[str]:
    base = forge_root(root) / "tasks"
    if not base.is_dir():
        return []
    return sorted(path.name for path in base.iterdir() if path.is_dir())


def write_handoff(root: Path, handoff: ForgeHandoff) -> Path:
    directory = forge_root(root) / "handoffs"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{handoff.handoff_id}.json"
    if path.exists():
        raise ContractError(
            "AF-FORGE-HANDOFF-EXISTS", f"handoff {handoff.handoff_id!r} already exists"
        )
    path.write_text(handoff.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_handoff(root: Path, handoff_id: str) -> ForgeHandoff:
    path = forge_root(root) / "handoffs" / f"{handoff_id}.json"
    if not path.is_file():
        raise ContractError("AF-FORGE-HANDOFF-NOT-FOUND", f"no handoff {handoff_id!r} under {root}")
    try:
        return ForgeHandoff.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise ContractError("AF-FORGE-STORE", f"{path}: {exc}") from exc


__all__ = [
    "append_event",
    "create_task",
    "forge_root",
    "load_handoff",
    "load_request",
    "load_status",
    "task_dir",
    "task_ids",
    "write_handoff",
    "write_status",
]
