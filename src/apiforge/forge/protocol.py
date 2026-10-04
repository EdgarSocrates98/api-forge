"""§46–§48 Forge Protocol: the public façade other engines will speak to.

Seven operations, all deterministic and local:

- ``discover_capabilities`` — project the public capability matrix;
- ``submit_task`` — validate against the matrix + declared risk gate, then
  persist the request and an ``accepted`` status (events stay append-only);
- ``attach_task`` — link a governed TaskSpec id to a forge task;
- ``inspect_task`` — live projection: forge state derived from the governed
  task when one is linked;
- ``retrieve_result`` — map the governed OutcomeBrief, or ``unresolved``
  with the missing pieces named;
- ``retrieve_evidence`` — content-addressed artifact bundle (path + sha256);
- ``prepare_handoff`` — a portable ``ForgeHandoff`` bundle, always
  ``delivery: prepared`` — v1 never performs a live cross-engine call;
- ``health`` — declared counts plus honest store state.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from apiforge.capabilities.registry import load_capabilities
from apiforge.contracts.base import ContractError
from apiforge.contracts.forge_protocol import (
    ForgeCapabilityDescriptor,
    ForgeEvidenceArtifact,
    ForgeEvidenceBundle,
    ForgeHandoff,
    ForgeHealth,
    ForgeResultStatus,
    ForgeTaskRequest,
    ForgeTaskResult,
    ForgeTaskState,
    ForgeTaskStatus,
)
from apiforge.contracts.task import TaskState
from apiforge.forge import store

POLICY_INVALID_CODE = "AF-FORGE-POLICY"
POLICY_PATH = Path(__file__).resolve().parents[1] / "rules" / "forge_protocol.yaml"

# Governed TaskState -> the small wire lifecycle. detail stays visible via
# ForgeTaskStatus.governed_state — nothing is hidden by the projection.
_GOVERNED_TO_FORGE: dict[TaskState, ForgeTaskState] = {
    TaskState.DRAFT: "in_progress",
    TaskState.REVIEWED: "in_progress",
    TaskState.SEALED: "in_progress",
    TaskState.READY: "in_progress",
    TaskState.RUNNING: "in_progress",
    TaskState.PARKED: "in_progress",
    TaskState.AWAITING_SUPERVISION: "in_progress",
    TaskState.ACCEPTED: "completed",
    TaskState.REJECTED: "refused",
    TaskState.BLOCKED: "failed",
    TaskState.EXPIRED: "failed",
}

_BRIEF_TO_FORGE: dict[str, ForgeResultStatus] = {
    "DONE": "ok",
    "REVIEW": "review",
    "DECIDE": "review",
    "BLOCKED": "blocked",
    "FAILED": "failed",
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _load_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or POLICY_PATH
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: {exc}") from exc
    if not isinstance(raw.get("engine"), str) or not isinstance(raw.get("protocol_version"), str):
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: engine/protocol_version required")
    if not isinstance(raw.get("risk_gate"), list) or not isinstance(raw.get("engines"), list):
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: risk_gate/engines lists required")
    return dict(raw)


def discover_capabilities() -> tuple[ForgeCapabilityDescriptor, ...]:
    """Project the public capability matrix into wire descriptors."""
    return tuple(
        ForgeCapabilityDescriptor(
            capability_id=record.capability_id,
            operation=record.operation,
            state=record.state,
            risk=record.risk,
            surfaces=tuple(record.surfaces),
            evidence=tuple(record.evidence),
            limitations=tuple(record.limitations),
        )
        for record in load_capabilities()
    )


def submit_task(
    root: Path,
    request: ForgeTaskRequest,
    *,
    acknowledge_risk: bool = False,
    policy: Mapping[str, Any] | None = None,
) -> ForgeTaskStatus:
    """Validate + persist a forge task; refused submissions persist nothing."""
    rules = dict(policy) if policy is not None else _load_policy()
    known = {row.capability_id for row in load_capabilities()}
    if request.capability_id not in known:
        raise ContractError(
            "AF-FORGE-CAPABILITY-UNKNOWN",
            f"capability {request.capability_id!r} is not on the public matrix",
        )
    gated = set(rules.get("risk_gate") or ())
    if request.risk in gated and not acknowledge_risk:
        raise ContractError(
            "AF-FORGE-RISK-GATE",
            f"risk {request.risk} requires --acknowledge-risk at submit",
        )
    status = ForgeTaskStatus(task_id=request.task_id, state="accepted", updated_at=_now())
    store.create_task(Path(root), request, status)
    return status


def attach_task(root: Path, task_id: str, governed_task_id: str) -> ForgeTaskStatus:
    """Link a forge task to a governed TaskSpec; the governed task must exist."""
    root = Path(root)
    status = store.load_status(root, task_id)
    if status.state in ("completed", "failed", "refused"):
        raise ContractError(
            "AF-FORGE-STATE",
            f"forge task {task_id!r} is {status.state} — attach refused",
        )
    from apiforge.taskspec import store as taskstore

    spec = taskstore.load(root, governed_task_id)  # raises AF-TASK-NOT-FOUND
    updated = status.model_copy(
        update={
            "state": _GOVERNED_TO_FORGE[spec.state],
            "governed_task_id": governed_task_id,
            "governed_state": spec.state.value,
            "revision": status.revision + 1,
            "updated_at": _now(),
        }
    )
    store.write_status(store.task_dir(root, task_id), updated)
    store.append_event(
        store.task_dir(root, task_id),
        {
            "event": "attach",
            "governed_task_id": governed_task_id,
            "governed_state": spec.state.value,
            "at": updated.updated_at,
        },
    )
    return updated


def _project(status: ForgeTaskStatus, root: Path) -> ForgeTaskStatus:
    """Live-projection: derive the forge state from the linked governed task."""
    if status.governed_task_id is None:
        return status
    from apiforge.taskspec import store as taskstore

    try:
        spec = taskstore.load(root, status.governed_task_id)
    except ContractError:
        return status.model_copy(
            update={
                "state": "unresolved",
                "unresolved": (
                    *status.unresolved,
                    f"governed task {status.governed_task_id!r} not found — link broken",
                ),
            }
        )
    return status.model_copy(
        update={
            "state": _GOVERNED_TO_FORGE[spec.state],
            "governed_state": spec.state.value,
        }
    )


def inspect_task(root: Path, task_id: str) -> ForgeTaskStatus:
    """Current wire projection — live state, not the last persisted row."""
    return _project(store.load_status(Path(root), task_id), Path(root))


def retrieve_result(root: Path, task_id: str) -> ForgeTaskResult:
    """Map the governed OutcomeBrief when a governed task is linked."""
    root = Path(root)
    status = inspect_task(root, task_id)
    if status.governed_task_id is None:
        return ForgeTaskResult(
            task_id=task_id,
            status="unresolved",
            gaps=("no governed task attached — `forge attach` first",),
        )
    from pydantic import ValidationError

    from apiforge.brief.render import brief_for_task

    try:
        brief = brief_for_task(root, status.governed_task_id)
    except (ContractError, ValidationError) as exc:
        return ForgeTaskResult(
            task_id=task_id,
            status="unresolved",
            payload={"governed_task_id": status.governed_task_id},
            gaps=(f"governed brief unavailable: {exc}",),
        )
    payload: dict[str, Any] = {
        "governed_task_id": status.governed_task_id,
        "outcome": brief.outcome,
        "subject": brief.subject,
    }
    if brief.human_action:
        payload["human_action"] = brief.human_action
    return ForgeTaskResult(
        task_id=task_id,
        status=_BRIEF_TO_FORGE.get(brief.status.value, "unresolved"),
        payload=payload,
        evidence=tuple(brief.proof),
        gaps=tuple(brief.gaps),
        limitations=tuple(brief.open),
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def retrieve_evidence(root: Path, task_id: str) -> ForgeEvidenceBundle:
    """Content-addressed bundle: every declared artifact hashed, gaps named."""
    root = Path(root)
    status = inspect_task(root, task_id)
    artifacts: list[ForgeEvidenceArtifact] = []
    unresolved: list[str] = []

    forge_dir = store.task_dir(root, task_id)
    for name, kind in (
        ("request.json", "request"),
        ("status.json", "status"),
        ("events.jsonl", "ledger"),
    ):
        path = forge_dir / name
        if path.is_file():
            artifacts.append(
                ForgeEvidenceArtifact(
                    path=str(path.relative_to(root)),
                    sha256=_sha256(path),
                    kind=kind,
                )
            )
        else:
            unresolved.append(f"forge artifact {name} missing")

    if status.governed_task_id is not None:
        from apiforge.taskspec import store as taskstore

        governed = taskstore.task_dir(root, status.governed_task_id)
        if governed.is_dir():
            for path in sorted(governed.rglob("*")):
                if path.is_file():
                    artifacts.append(
                        ForgeEvidenceArtifact(
                            path=str(path.relative_to(root)),
                            sha256=_sha256(path),
                            kind="governed",
                        )
                    )
        else:
            unresolved.append(f"governed task dir {status.governed_task_id!r} absent — link broken")
    else:
        unresolved.append("no governed task attached — governed evidence absent")

    return ForgeEvidenceBundle(
        task_id=task_id,
        artifacts=tuple(artifacts),
        produced_at=_now(),
        unresolved=tuple(unresolved),
    )


def prepare_handoff(
    root: Path,
    task_id: str,
    to_engine: str,
    *,
    context_refs: tuple[str, ...] = (),
    policy: Mapping[str, Any] | None = None,
) -> ForgeHandoff:
    """Portable cross-engine bundle — delivery stays a human/transport step."""
    rules = dict(policy) if policy is not None else _load_policy()
    declared = set(rules.get("engines") or ())
    if to_engine not in declared:
        raise ContractError(
            "AF-FORGE-ENGINE-UNKNOWN",
            f"engine {to_engine!r} not declared in rules/forge_protocol.yaml",
        )
    root = Path(root)
    request = store.load_request(root, task_id)
    status = inspect_task(root, task_id)
    bundle = retrieve_evidence(root, task_id)
    handoff = ForgeHandoff(
        handoff_id=f"{task_id}-to-{to_engine}",
        task_id=task_id,
        from_engine=str(rules.get("engine", "api-forge")),
        to_engine=to_engine,
        request=request,
        status=status,
        evidence_refs=tuple(f"{a.path}#sha256:{a.sha256[:12]}" for a in bundle.artifacts),
        context_refs=context_refs,
        created_at=_now(),
        unresolved=(
            *bundle.unresolved,
            "delivery is a human/transport step — no live cross-engine call made",
        ),
    )
    store.write_handoff(root, handoff)
    store.append_event(
        store.task_dir(root, task_id),
        {
            "event": "handoff-prepared",
            "handoff_id": handoff.handoff_id,
            "to_engine": to_engine,
            "at": handoff.created_at,
        },
    )
    return handoff


def health(root: Path) -> ForgeHealth:
    """Declared counts + honest store state — degraded on a corrupt row."""
    root = Path(root)
    rules = _load_policy()
    by_state: dict[str, int] = {}
    unresolved: list[str] = []
    state = "ok"
    for task_id in store.task_ids(root):
        try:
            projected = inspect_task(root, task_id)
        except ContractError as exc:
            unresolved.append(f"{task_id}: {exc}")
            state = "degraded"
            continue
        by_state[projected.state] = by_state.get(projected.state, 0) + 1
    return ForgeHealth(
        engine=str(rules.get("engine", "api-forge")),
        protocol_version=str(rules.get("protocol_version", "forge-protocol/v1")),
        state=state,  # type: ignore[arg-type]
        capabilities=len(load_capabilities()),
        tasks_by_state=by_state,
        unresolved=tuple(unresolved),
    )


__all__ = [
    "attach_task",
    "discover_capabilities",
    "health",
    "inspect_task",
    "prepare_handoff",
    "retrieve_evidence",
    "retrieve_result",
    "submit_task",
]
