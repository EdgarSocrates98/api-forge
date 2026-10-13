"""Human annotation and blind verifier verdicts; closed enums only.

A verdict is stored as a receipt bound to the annotation digest; any later
annotation change makes it stale instead of silently re-labelling it verified.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from apiforge.contracts.field import EXIT_REASONS, FieldPhase, FieldRun, VerificationReceipt
from apiforge.field import readiness
from apiforge.field.actors import parse_actor, same_actor
from apiforge.field.corpus import load_corpus
from apiforge.field.errors import ENUM, VERIFIER_NOT_INDEPENDENT, FieldError
from apiforge.field.identity import ensure_cycle
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
    root = Path(root)
    ensure_cycle(root, load_corpus(root))
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
    return _update(root, run, changes)


def verify(
    root: Path,
    *,
    task_id: str,
    phase: str,
    verdict: str,
    verifier: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    root = Path(root)
    ensure_cycle(root, load_corpus(root))
    checked_phase: FieldPhase = _enum(phase, PHASES, "phase")  # type: ignore[assignment]
    checked = _enum(verdict, VERDICTS, "verdict")
    actor = parse_actor(verifier, field="verifier")
    run = load_run(root, task_id, checked_phase)
    if same_actor(actor, run.executor):
        raise FieldError(
            VERIFIER_NOT_INDEPENDENT,
            f"verifier {actor.kind}:{actor.id} is the executor of {task_id}",
            field="verifier",
            unlock="verify with a different human or agent than the executor",
        )
    receipt = VerificationReceipt(
        verdict=checked,  # type: ignore[arg-type]
        annotation_sha256=readiness.annotation_digest(run),
        verifier=actor,
        verified_at=readiness.stamp(now or readiness.utc_now()),
    )
    updated = _update(root, run, {"verification": receipt.model_dump(mode="json")})
    return {
        "task_id": updated.task_id,
        "phase": updated.phase,
        "verifier_verdict": receipt.verdict,
        "verifier_kind": actor.kind,
        "verified_at": receipt.verified_at,
    }


__all__ = ["PHASES", "VERDICTS", "annotate", "verify"]
