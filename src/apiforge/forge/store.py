"""Forge task persistence: ``<root>/.apiforge/forge/`` — append-only, JSON only.

Layout::

    forge/tasks/<task_id>/request.json   ForgeTaskRequest (immutable)
    forge/tasks/<task_id>/status.json    ForgeTaskStatus (last persisted)
    forge/tasks/<task_id>/events.jsonl   append-only transitions
    forge/handoffs/<handoff_id>.json     ForgeHandoff bundles
    forge/delegations/<run_id>/record.json    DoctorDelegationRecord (lf-0030)
    forge/delegations/<run_id>/scan.json      parsed doctor scan (when it ran)
    forge/delegations/<run_id>/scan.agent.txt parsed-row projection of stdout
    forge/delegations/<run_id>/compare-*.json before/after ScanDelta artifacts
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.delegation import DoctorDelegationRecord
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


# ---------------------------------------------------------------------------
# Doctor delegation records (lf-0030) — same append-only discipline
# ---------------------------------------------------------------------------

_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def delegation_dir(root: Path, run_id: str) -> Path:
    return forge_root(root) / "delegations" / run_id


def _valid_run_id(run_id: str) -> None:
    if not _RUN_ID.match(run_id):
        raise ContractError(
            "AF-DELEG-RUN-ID",
            f"delegation run id {run_id!r} must match {_RUN_ID.pattern}",
        )


def write_delegation(root: Path, record: DoctorDelegationRecord) -> Path:
    """Persist a delegation record; an existing run id is refused."""
    _valid_run_id(record.run_id)
    directory = delegation_dir(root, record.run_id)
    if directory.exists():
        raise ContractError("AF-DELEG-EXISTS", f"delegation run {record.run_id!r} already exists")
    directory.mkdir(parents=True)
    (directory / "record.json").write_text(record.model_dump_json(indent=2), encoding="utf-8")
    append_event(
        directory,
        {"event": "delegation-recorded", "status": record.status, "at": record.created_at},
    )
    return directory


def rewrite_delegation(root: Path, record: DoctorDelegationRecord) -> Path:
    """Rewrite the record of an existing run — only for result_refs sealing."""
    directory = delegation_dir(root, record.run_id)
    if not directory.is_dir():
        raise ContractError(
            "AF-DELEG-NOT-FOUND", f"no delegation run {record.run_id!r} under {root}"
        )
    (directory / "record.json").write_text(record.model_dump_json(indent=2), encoding="utf-8")
    return directory


def load_delegation(root: Path, run_id: str) -> DoctorDelegationRecord:
    path = delegation_dir(root, run_id) / "record.json"
    if not path.is_file():
        raise ContractError("AF-DELEG-NOT-FOUND", f"no delegation run {run_id!r} under {root}")
    try:
        return DoctorDelegationRecord.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise ContractError("AF-DELEG-STORE", f"{path}: {exc}") from exc


def delegation_ids(root: Path) -> list[str]:
    base = forge_root(root) / "delegations"
    if not base.is_dir():
        return []
    return sorted(path.name for path in base.iterdir() if path.is_dir())


__all__ = [
    "append_event",
    "create_task",
    "delegation_dir",
    "delegation_ids",
    "forge_root",
    "load_delegation",
    "load_handoff",
    "load_request",
    "load_status",
    "rewrite_delegation",
    "task_dir",
    "task_ids",
    "write_delegation",
    "write_handoff",
    "write_status",
]
