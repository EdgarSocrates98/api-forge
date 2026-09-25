"""Canonical read-only projections for every user-facing surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

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
    canonical_payload = dict(payload)
    runtime_payload = canonical_payload.get("runtime")
    if isinstance(runtime_payload, dict):
        for key in ("routing", "routing_plan", "routing_errors"):
            if key not in canonical_payload and key in runtime_payload:
                canonical_payload[key] = runtime_payload[key]
    routing = canonical_payload.get("routing")
    plan = canonical_payload.get("routing_plan")
    gaps_value = canonical_payload.get("gaps", ())
    refs_value = canonical_payload.get("evidence_refs", ())
    gaps_values: list[object] = list(gaps_value) if isinstance(gaps_value, (list, tuple)) else []
    refs_values: list[object] = list(refs_value) if isinstance(refs_value, (list, tuple)) else []
    if isinstance(routing, dict):
        gaps_values.extend(routing.get("unresolved", ()))
        refs_values.extend(routing.get("evidence", ()))
        assessment = routing.get("risk_complexity")
        if isinstance(assessment, dict):
            gaps_values.extend(assessment.get("unresolved", ()))
            refs_values.extend(assessment.get("evidence", ()))
    if isinstance(plan, dict):
        gaps_values.extend(plan.get("unresolved", ()))
        refs_values.extend(plan.get("evidence", ()))
    gaps_raw = gaps_values
    refs_raw = refs_values
    gaps = tuple(str(item) for item in gaps_raw) if isinstance(gaps_raw, (list, tuple)) else ()
    refs = tuple(str(item) for item in refs_raw) if isinstance(refs_raw, (list, tuple)) else ()
    status = _status(
        canonical_payload.get("status", canonical_payload.get("final_status", "REVIEW"))
    )
    if status not in {"READY", "RUNNING", "DONE", "REVIEW", "BLOCKED", "UNRESOLVED"}:
        status = "REVIEW"
    evidence_level = "verified" if payload.get("run_digest") else "observed"
    view = ExperienceView(
        task_id=task_id,
        status=status,  # type: ignore[arg-type]
        title=str(canonical_payload.get("title", "API Forge")),
        summary=str(canonical_payload.get("summary", canonical_payload.get("message", ""))),
        gaps=gaps,
        actions=("evolve", "resume", "review", "doctor"),
        evidence_refs=refs,
        evidence=EvidenceRecord(
            level=evidence_level,  # type: ignore[arg-type]
            source="runtime-experience",
            refs=refs,
            limitations=tuple(gaps),
        ),
        routing=routing if isinstance(routing, dict) else None,
        routing_plan=plan if isinstance(plan, dict) else None,
        payload=canonical_payload,
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


def project_result(task_id: str, result: object, *, surface: str = "json") -> ExperienceSnapshot:
    """Project a new canonical application result without adding semantics."""

    if hasattr(result, "model_dump"):
        payload = cast(Any, result).model_dump(mode="json")
    elif isinstance(result, dict):
        payload = result
    else:
        raise TypeError(f"unsupported projection result: {type(result).__name__}")
    return project_payload(task_id, payload, surface=surface)
