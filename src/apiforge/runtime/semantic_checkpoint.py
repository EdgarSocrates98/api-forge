"""Persistence and equivalence helpers for semantic resume checkpoints."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from apiforge.contracts.agentic_memory import SemanticCheckpoint


def _path(root: Path, task_id: str, run_id: str) -> Path:
    base = Path(root).resolve()
    if base.name == ".apiforge":
        base = base.parent
    return base / ".apiforge" / "runtime" / "checkpoints" / task_id / f"{run_id}.json"


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_checkpoint(
    *,
    task_id: str,
    run_id: str,
    task_state: str,
    current_objective: str,
    created_at: str,
    decisions_accepted: tuple[str, ...] = (),
    decisions_rejected: tuple[str, ...] = (),
    facts_still_valid: tuple[str, ...] = (),
    assumptions: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
    working_set: tuple[str, ...] = (),
    artifact_refs: tuple[str, ...] = (),
    memory_refs: tuple[str, ...] = (),
    tool_state: dict[str, object] | None = None,
    routing_state: dict[str, object] | None = None,
    budget_state: dict[str, object] | None = None,
    next_actions: tuple[str, ...] = (),
    risk_state: dict[str, object] | None = None,
) -> SemanticCheckpoint:
    body = {
        "task_id": task_id,
        "run_id": run_id,
        "task_state": task_state,
        "current_objective": current_objective,
        "decisions_accepted": decisions_accepted,
        "decisions_rejected": decisions_rejected,
        "facts_still_valid": facts_still_valid,
        "assumptions": assumptions,
        "unresolved": unresolved,
        "working_set": working_set,
        "artifact_refs": artifact_refs,
        "memory_refs": memory_refs,
        "tool_state": tool_state or {},
        "routing_state": routing_state or {},
        "budget_state": budget_state or {},
        "next_actions": next_actions,
        "risk_state": risk_state or {},
        "created_at": created_at,
    }
    payload = body | {
        "checkpoint_id": "checkpoint:" + _digest(body)[:16],
        "content_sha256": _digest(body),
    }
    return SemanticCheckpoint.model_validate(payload)


def save_checkpoint(root: Path, checkpoint: SemanticCheckpoint) -> Path:
    path = _path(root, checkpoint.task_id, checkpoint.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(checkpoint.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return path


def load_checkpoint(root: Path, task_id: str, run_id: str) -> SemanticCheckpoint:
    path = _path(root, task_id, run_id)
    if not path.is_file():
        raise ValueError(f"AF-CHECKPOINT-NOT-FOUND: {path}")
    return SemanticCheckpoint.model_validate_json(path.read_text(encoding="utf-8"))


def equivalent(left: SemanticCheckpoint, right: SemanticCheckpoint) -> bool:
    """Compare effective state, excluding identity and creation time."""
    ignored = {"checkpoint_id", "content_sha256", "created_at"}
    l = left.model_dump(mode="json")
    r = right.model_dump(mode="json")
    return {k: v for k, v in l.items() if k not in ignored} == {
        k: v for k, v in r.items() if k not in ignored
    }


__all__ = ["build_checkpoint", "equivalent", "load_checkpoint", "save_checkpoint"]
