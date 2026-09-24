"""Canonical read-only projections for every user-facing surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.application import runtime_experience
from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.experience import ExperienceAction, ExperienceSnapshot, ExperienceView

_STATUS_ALIASES = {
    "completed": "DONE",
    "complete": "DONE",
    "success": "DONE",
    "failed": "REVIEW",
    "error": "REVIEW",
    "pending": "RUNNING",
    "unresolved": "UNRESOLVED",
    "blocked": "BLOCKED",
}


def _status(value: object) -> str:
    normalized = str(value or "REVIEW").upper()
    return _STATUS_ALIASES.get(normalized.lower(), normalized)


def project_payload(
    task_id: str, payload: dict[str, Any], *, surface: str = "json"
) -> ExperienceSnapshot:
    """Normalize a legacy application payload without mutating it."""
    gaps_raw = payload.get("gaps", ())
    refs_raw = payload.get("evidence_refs", ())
    gaps = tuple(str(item) for item in gaps_raw) if isinstance(gaps_raw, (list, tuple)) else ()
    refs = tuple(str(item) for item in refs_raw) if isinstance(refs_raw, (list, tuple)) else ()
    status = _status(payload.get("status", payload.get("final_status", "REVIEW")))
    if status not in {"READY", "RUNNING", "DONE", "REVIEW", "BLOCKED", "UNRESOLVED"}:
        status = "REVIEW"
    evidence_level = "verified" if payload.get("run_digest") else "observed"
    view = ExperienceView(
        task_id=task_id,
        status=status,  # type: ignore[arg-type]
        title=str(payload.get("title", "API Forge")),
        summary=str(payload.get("summary", payload.get("message", ""))),
        gaps=gaps,
        actions=("evolve", "resume", "review", "doctor"),
        evidence_refs=refs,
        evidence=EvidenceRecord(
            level=evidence_level,  # type: ignore[arg-type]
            source="runtime-experience",
            refs=refs,
            limitations=tuple(gaps),
        ),
        payload=dict(payload),
    )
    actions = tuple(
        ExperienceAction(name=name, label=name.capitalize(), safe=name in {"review", "doctor"})
        for name in view.actions
    )
    return ExperienceSnapshot(view=view, actions=actions, surface=surface)


def project_status(root: Path, task_id: str, *, surface: str = "json") -> ExperienceSnapshot:
    """Read and project the canonical runtime status."""
    return project_payload(task_id, runtime_experience.status(root, task_id), surface=surface)


def project_doctor(root: Path, task_id: str, *, surface: str = "json") -> ExperienceSnapshot:
    return project_payload(task_id, runtime_experience.doctor(root, task_id), surface=surface)


def project_review(root: Path, task_id: str, *, surface: str = "json") -> ExperienceSnapshot:
    return project_payload(task_id, runtime_experience.review(root, task_id), surface=surface)
