"""Economic checkpoint (§104): what a run already spent, so a resume continues it.

``execute_run`` writes ``economy_checkpoint.json`` next to ``summary.json``;
``resume_existing_run`` reads it, pins the effective profile (a resume can
raise the profile, never lower it) and rewrites it with the cumulative spend.
"""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import EconomyPlan
from apiforge.contracts.economy_resume import EconomyCheckpoint
from apiforge.runtime.economy import PROFILES

CHECKPOINT_FILE = "economy_checkpoint.json"
RESUME_PINNED = "AF-ECONOMY-RESUME-PINNED"


def _refusal(code: str, detail: str, field: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = field  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def build_checkpoint(
    *,
    run_id: str,
    task_id: str,
    plan: EconomyPlan,
    max_calls: int,
    calls_used: int,
    stopped_at: str | None,
    now: str,
    resumes: int = 0,
    codes: tuple[str, ...] = (),
) -> EconomyCheckpoint:
    exhausted = calls_used >= max_calls
    all_codes = set(codes) | ({"AF-BUDGET-EXHAUSTED"} if exhausted else set())
    return EconomyCheckpoint(
        run_id=run_id,
        task_id=task_id,
        requested=plan.requested,
        effective=plan.effective,
        max_calls=max_calls,
        calls_used=calls_used,
        calls_remaining=max(0, max_calls - calls_used),
        stopped_at=stopped_at,
        resumes=resumes,
        updated_at=now,
        status="unresolved" if exhausted or codes else "ok",
        codes=tuple(sorted(all_codes)),
    )


def save_checkpoint(directory: Path, checkpoint: EconomyCheckpoint) -> Path:
    path = Path(directory) / CHECKPOINT_FILE
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(
        json.dumps(checkpoint.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)
    return path


def load_checkpoint(directory: Path) -> EconomyCheckpoint | None:
    path = Path(directory) / CHECKPOINT_FILE
    if not path.is_file():
        return None
    try:
        return EconomyCheckpoint.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        raise _refusal(
            "AF-ECONOMY-CHECKPOINT-INVALID",
            f"{path}: {exc}",
            "checkpoint",
            "restore the run directory or delete the checkpoint to resume without prior spend",
        ) from exc


def pin_profile(
    checkpoint: EconomyCheckpoint | None, requested: str | None
) -> tuple[str | None, tuple[str, ...]]:
    """A resume keeps at least the profile the run already escalated to."""
    if checkpoint is None:
        return requested, ()
    if requested is None or PROFILES.index(requested) < PROFILES.index(checkpoint.effective):
        notes = (
            ()
            if requested is None
            else (
                (
                    f"{RESUME_PINNED}: requested {requested} is below the checkpoint "
                    f"profile {checkpoint.effective}; the resume keeps {checkpoint.effective}"
                ),
            )
        )
        return checkpoint.effective, notes
    return requested, ()


def show_checkpoint(root: Path, task_id: str, run_id: str) -> EconomyCheckpoint:
    from apiforge.taskspec import store as task_store

    directory = task_store.task_dir(Path(root), task_id) / "runs" / run_id.replace(":", "-")
    checkpoint = load_checkpoint(directory)
    if checkpoint is None:
        raise _refusal(
            "AF-ECONOMY-CHECKPOINT-NOT-FOUND",
            f"run {run_id!r} of task {task_id!r} has no economy checkpoint",
            "run_id",
            "run it with `apiforge runtime run` (economy runs write a checkpoint)",
        )
    return checkpoint


__all__ = [
    "CHECKPOINT_FILE",
    "build_checkpoint",
    "load_checkpoint",
    "pin_profile",
    "save_checkpoint",
    "show_checkpoint",
]
