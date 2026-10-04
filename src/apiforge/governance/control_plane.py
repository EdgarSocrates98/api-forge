"""§28-§32 Decision Control Plane: shadow/assisted/active lifecycle + fallback.

Routes are declared in ``rules/control_plane.yaml``. The lifecycle state is
an append-only overlay (``control-plane/modes.jsonl``); shadow observations
live in ``control-plane/shadow.jsonl``. The declared yaml is never mutated —
the latest overlay row wins.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml
from pydantic import BaseModel

from apiforge.contracts.agentic import ApprovalGate
from apiforge.contracts.agentic_governance import (
    ControlPlaneMode,
    ControlPlaneRoute,
    FallbackDecision,
    FallbackTrigger,
    PromotionDecision,
    PromotionEvidence,
    RouteDecision,
    ShadowRecord,
)
from apiforge.economy.run_ledger import EconomyError

RULES = Path(__file__).resolve().parent.parent / "rules" / "control_plane.yaml"
_DIR = Path(".apiforge") / "control-plane"
_MODES = "modes.jsonl"
_SHADOW = "shadow.jsonl"

ROUTE_UNKNOWN = "AF-GOV-ROUTE-UNKNOWN"
TRANSITION_INVALID = "AF-GOV-MODE-TRANSITION-INVALID"
PROMOTION_INCOMPLETE = "AF-GOV-PROMOTION-INCOMPLETE"
PROMOTION_NOT_APPROVED = "AF-GOV-PROMOTION-NOT-APPROVED"
FALLBACK_MISSING = "AF-GOV-FALLBACK-MISSING"
STORE_CORRUPT = "AF-GOV-STORE-CORRUPT"

_ORDER: dict[ControlPlaneMode, int] = {"shadow": 0, "assisted": 1, "active": 2}
_FALLBACK_TRIGGERS: tuple[FallbackTrigger, ...] = (
    "low_confidence",
    "missing_evidence",
    "security_issue",
    "provider_issue",
    "budget_issue",
)


def load_routes(path: Path | None = None) -> dict[str, ControlPlaneRoute]:
    data = yaml.safe_load((path or RULES).read_text(encoding="utf-8")) or {}
    routes: dict[str, ControlPlaneRoute] = {}
    for row in data.get("routes") or ():
        route = ControlPlaneRoute.model_validate(row)
        routes[route.route] = route
    return routes


def _directory(root: Path) -> Path:
    resolved = Path(root).resolve()
    if resolved.name == ".apiforge":
        resolved = resolved.parent
    return resolved / _DIR


def _rows[T: BaseModel](path: Path, model: type[T]) -> list[T]:
    if not path.is_file():
        return []
    rows: list[Any] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(model.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValueError) as exc:
            raise EconomyError(
                STORE_CORRUPT,
                f"{path}:{line_no}: {exc}",
                field=str(path),
                unlock="repair or remove the corrupt ledger row",
            ) from exc
    return rows


def _append(root: Path, name: str, payload: dict[str, object]) -> None:
    directory = _directory(root)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / name).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True))
        handle.write("\n")


def route_status(
    root: Path, route_name: str, *, routes: dict[str, ControlPlaneRoute] | None = None
) -> ControlPlaneRoute:
    """The declared route overlaid with the latest recorded mode."""
    declared = (routes or load_routes()).get(route_name)
    if declared is None:
        raise EconomyError(
            ROUTE_UNKNOWN,
            f"route '{route_name}' is not declared in the control-plane rules",
            field="route",
            unlock="declare the route in rules/control_plane.yaml",
        )
    latest = declared.mode
    promoted_at = declared.promoted_at
    approval_id = declared.promotion_approval_id
    for row in _rows(_directory(root) / _MODES, _ModeRow):
        if row.route == route_name:
            latest = row.mode
            promoted_at = row.promoted_at
            approval_id = row.promotion_approval_id
    return declared.model_copy(
        update={"mode": latest, "promoted_at": promoted_at, "promotion_approval_id": approval_id}
    )


def all_routes(
    root: Path, *, routes: dict[str, ControlPlaneRoute] | None = None
) -> list[ControlPlaneRoute]:
    declared = routes or load_routes()
    return [route_status(root, name, routes=declared) for name in declared]


def diff_decisions(candidate: dict[str, object], legacy: dict[str, object]) -> tuple[str, ...]:
    """Sorted top-level field paths where the two decisions differ."""
    keys = set(candidate) | set(legacy)
    return tuple(sorted(key for key in keys if candidate.get(key) != legacy.get(key)))


def record_shadow(root: Path, record: ShadowRecord) -> dict[str, object]:
    """Append a §29 shadow record; the candidate never governs here."""
    _append(root, _SHADOW, record.model_dump(mode="json"))
    return {"status": "recorded", "record": record.model_dump(mode="json")}


def shadow_records(root: Path, route: str | None = None) -> list[ShadowRecord]:
    rows = _rows(_directory(root) / _SHADOW, ShadowRecord)
    return [row for row in rows if route is None or row.route == route]


def detect_triggers(
    *,
    confidence: float | None,
    evidence_complete: bool,
    security_issue: bool,
    provider_issue: bool,
    budget_issue: bool,
    min_confidence: float = 0.5,
) -> tuple[FallbackTrigger, ...]:
    """§32 declared signal -> trigger mapping; absent confidence stays quiet."""
    triggers: list[FallbackTrigger] = []
    if confidence is not None and confidence < min_confidence:
        triggers.append("low_confidence")
    if not evidence_complete:
        triggers.append("missing_evidence")
    if security_issue:
        triggers.append("security_issue")
    if provider_issue:
        triggers.append("provider_issue")
    if budget_issue:
        triggers.append("budget_issue")
    return tuple(triggers)


def select_fallback(route: ControlPlaneRoute, trigger: FallbackTrigger | None) -> FallbackDecision:
    if trigger is None:
        return FallbackDecision(
            route=route.route, trigger=None, action="continue_active", reason="no trigger"
        )
    if route.fallback_route:
        return FallbackDecision(
            route=route.route,
            trigger=trigger,
            action="use_fallback",
            fallback_route=route.fallback_route,
            reason=f"{trigger} on active route; declared fallback engaged",
        )
    return FallbackDecision(
        route=route.route,
        trigger=trigger,
        action="refuse",
        code=FALLBACK_MISSING,
        reason="active route degraded and no fallback is declared; refusing (fail-closed)",
    )


def evaluate_route(
    root: Path,
    route_name: str,
    *,
    candidate_decision: dict[str, object] | None = None,
    legacy_decision: dict[str, object] | None = None,
    confidence: float | None = None,
    evidence_refs: tuple[str, ...] = (),
    triggers: tuple[FallbackTrigger, ...] = (),
    now: datetime | None = None,
    routes: dict[str, ControlPlaneRoute] | None = None,
) -> RouteDecision:
    """§29-§32 who governs this evaluation: never the candidate in shadow."""
    route = route_status(root, route_name, routes=routes)
    stamp = (now or datetime.now(UTC)).isoformat()
    candidate = candidate_decision or {}
    legacy = legacy_decision or {}
    if route.mode == "shadow":
        record = ShadowRecord(
            route=route.route,
            candidate_decision=candidate,
            legacy_decision=legacy,
            difference=diff_decisions(candidate, legacy),
            confidence=confidence,
            evidence_refs=evidence_refs,
            recorded_at=stamp,
        )
        record_shadow(root, record)
        return RouteDecision(
            route=route.route,
            mode="shadow",
            governing="legacy",
            shadow=True,
            reason="candidate ran in parallel and was recorded; legacy governs",
        )
    if route.mode == "assisted":
        return RouteDecision(
            route=route.route,
            mode="assisted",
            governing="legacy",
            recommendation=dict(candidate) if candidate else None,
            reason="candidate recommends; legacy/human remains authoritative",
        )
    fallback = select_fallback(route, triggers[0] if triggers else None)
    if fallback.action != "continue_active":
        return RouteDecision(
            route=route.route,
            mode="active",
            governing="none",
            fallback=fallback,
            reason=fallback.reason,
        )
    return RouteDecision(
        route=route.route,
        mode="active",
        governing="candidate",
        fallback=fallback,
        reason="active route; candidate governs",
    )


class _ModeRow(ControlPlaneRoute):
    """Append-only overlay row; subclass keeps validation identical."""


def promote(
    root: Path,
    route_name: str,
    evidence: PromotionEvidence,
    *,
    approval: ApprovalGate | None = None,
    now: datetime | None = None,
    routes: dict[str, ControlPlaneRoute] | None = None,
) -> PromotionDecision:
    """Move a route one lifecycle step forward; §31 gates the ACTIVE step."""
    if evidence.route != route_name:
        raise EconomyError(
            TRANSITION_INVALID,
            f"evidence.route '{evidence.route}' does not match '{route_name}'",
            field="route",
            unlock="pass a PromotionEvidence whose route matches the target route",
        )
    route = route_status(root, route_name, routes=routes)
    target: ControlPlaneMode = "assisted" if route.mode == "shadow" else "active"
    if route.mode == "active":
        return PromotionDecision(
            route=route_name,
            from_mode="active",
            to_mode="active",
            allowed=False,
            code=TRANSITION_INVALID,
            reason="route is already active; no forward step exists",
        )
    missing: list[str] = []
    if target == "assisted":
        if not evidence.evidence_complete:
            missing.append("evidence_complete")
    else:
        for field in (
            "eval_thresholds_passed",
            "security_gates_passed",
            "evidence_complete",
            "rollback_exists",
        ):
            if not getattr(evidence, field):
                missing.append(field)
        if evidence.approval_id is None:
            missing.append("approval_id")
    if missing:
        return PromotionDecision(
            route=route_name,
            from_mode=route.mode,
            to_mode=target,
            allowed=False,
            missing=tuple(missing),
            code=PROMOTION_INCOMPLETE,
            reason=f"promotion requirements unmet: {', '.join(missing)}",
        )
    if target == "active":
        approved = (
            approval is not None
            and approval.status == "approved"
            and approval.gate_id == evidence.approval_id
        )
        if not approved:
            return PromotionDecision(
                route=route_name,
                from_mode=route.mode,
                to_mode="active",
                allowed=False,
                code=PROMOTION_NOT_APPROVED,
                reason="active promotion requires an approved ApprovalGate "
                "matching evidence.approval_id",
            )
    stamp = (now or datetime.now(UTC)).isoformat()
    row = _ModeRow(
        route=route.route,
        mode=target,
        candidate=route.candidate,
        legacy=route.legacy,
        fallback_route=route.fallback_route,
        promoted_at=stamp,
        promotion_approval_id=evidence.approval_id,
    )
    _append(root, _MODES, row.model_dump(mode="json"))
    return PromotionDecision(
        route=route_name,
        from_mode=route.mode,
        to_mode=target,
        allowed=True,
        reason=f"route promoted {route.mode} -> {target}",
    )


def demote(
    root: Path,
    route_name: str,
    *,
    now: datetime | None = None,
    routes: dict[str, ControlPlaneRoute] | None = None,
) -> ControlPlaneRoute:
    """Step a route back one stage; demotion is always allowed (safe path)."""
    route = route_status(root, route_name, routes=routes)
    previous = cast(
        ControlPlaneMode,
        {"shadow": "shadow", "assisted": "shadow", "active": "assisted"}[route.mode],
    )
    stamp = (now or datetime.now(UTC)).isoformat()
    row = _ModeRow(
        route=route.route,
        mode=previous,
        candidate=route.candidate,
        legacy=route.legacy,
        fallback_route=route.fallback_route,
        promoted_at=stamp,
        promotion_approval_id=None,
    )
    _append(root, _MODES, row.model_dump(mode="json"))
    return route_status(root, route_name, routes=routes)


__all__ = [
    "FALLBACK_MISSING",
    "PROMOTION_INCOMPLETE",
    "PROMOTION_NOT_APPROVED",
    "ROUTE_UNKNOWN",
    "TRANSITION_INVALID",
    "all_routes",
    "demote",
    "detect_triggers",
    "diff_decisions",
    "evaluate_route",
    "load_routes",
    "promote",
    "record_shadow",
    "route_status",
    "select_fallback",
    "shadow_records",
]
