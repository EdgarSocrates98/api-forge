"""Human annotation and blind verifier verdicts; closed enums only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.contracts.field import EXIT_REASONS, FieldPhase, FieldRun
from apiforge.field.errors import ENUM, FieldError
from apiforge.field.store import load_run, save_run

VERDICTS = ("agree", "disagree", "unresolved")
PHASES = ("baseline", "ab_on")


def _enum(value: str, allowed: tuple[str, ...], field: str) -> str:
    if value not in allowed:
        raise FieldError(
            ENUM,
            f"{value!r} is not an allowed {field}",
            field=field,
            unlock=f"use one of: {', '.join(allowed)}",
        )
    return value


def _count(value: int, field: str) -> int:
    if value < 0:
        raise FieldError(
            ENUM, f"{field} must be >= 0", field=field, unlock="pass a non-negative integer"
        )
    return value


def _update(root: Path, run: FieldRun, changes: dict[str, Any]) -> FieldRun:
    updated = FieldRun.model_validate({**run.model_dump(mode="json"), **changes})
    save_run(root, updated)
    return updated


def annotate(
    root: Path,
    *,
    task_id: str,
    phase: str,
    task_completed: bool | None = None,
    exit_reason: str | None = None,
    manual_context_required: bool | None = None,
    human_intervention: bool | None = None,
    false_positives: int | None = None,
    false_negatives: int | None = None,
) -> FieldRun:
    checked_phase: FieldPhase = _enum(phase, PHASES, "phase")  # type: ignore[assignment]
    changes: dict[str, Any] = {}
    if exit_reason is not None:
        changes["exit_reason"] = _enum(exit_reason, EXIT_REASONS, "exit_reason")
    if task_completed is not None:
        changes["task_completed"] = task_completed
    if manual_context_required is not None:
        changes["manual_context_required"] = manual_context_required
    if human_intervention is not None:
        changes["human_intervention"] = human_intervention
    if false_positives is not None:
        changes["false_positives"] = _count(false_positives, "false_positives")
    if false_negatives is not None:
        changes["false_negatives"] = _count(false_negatives, "false_negatives")
    run = load_run(root, task_id, checked_phase)
    return _update(Path(root), run, changes)


def verify(root: Path, *, task_id: str, phase: str, verdict: str) -> dict[str, Any]:
    checked_phase: FieldPhase = _enum(phase, PHASES, "phase")  # type: ignore[assignment]
    checked = _enum(verdict, VERDICTS, "verdict")
    run = load_run(root, task_id, checked_phase)
    updated = _update(Path(root), run, {"verifier_verdict": checked})
    return {
        "task_id": updated.task_id,
        "phase": updated.phase,
        "verifier_verdict": updated.verifier_verdict,
    }


__all__ = ["PHASES", "VERDICTS", "annotate", "verify"]
