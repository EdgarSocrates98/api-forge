"""Economy Plane: profile resolution, risk floors, envelopes, trims and ladder decisions.

A profile is a preference; risk is an invariant. The effective profile is the
maximum of the requested profile and the floor derived from the routing
assessments, so risk can only escalate it. Trims remove optional capacity
(parallel slots, fallbacks, challengers) and never a role that risk requires.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import (
    BudgetEnvelope,
    EconomyPlan,
    EconomyProfile,
    LadderLevel,
    ProfileSource,
)
from apiforge.contracts.routing import RoutingDecision, RoutingPlan
from apiforge.contracts.task import TaskSpec

PROFILES: tuple[EconomyProfile, ...] = ("economy", "balanced", "deep")
LEVELS: tuple[LadderLevel, ...] = ("L0", "L1", "L2", "L3", "L4", "L5")
ROLE_KINDS = ("reviewer", "critic", "referee")
ESCALATED = "AF-ECONOMY-ESCALATED"


class EconomyError(ContractError):
    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


@dataclass(frozen=True)
class DeterministicProof:
    level: LadderLevel | None
    proofs: tuple[str, ...]
    missing: tuple[str, ...]
    run_ref: str | None = None


def _config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "rules" / "economy_profiles.yaml"


def load_economy_config(path: Path | None = None) -> dict[str, Any]:
    raw = yaml.safe_load((path or _config_path()).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict) or set(raw.get("profiles", {})) != set(PROFILES):
        raise ContractError("AF-RUNTIME-POLICY", "economy_profiles.yaml must define all profiles")
    return raw


def validate_profile(value: str | None) -> EconomyProfile | None:
    if value is None:
        return None
    if value not in PROFILES:
        raise EconomyError(
            "AF-ECONOMY-PROFILE-INVALID",
            f"profile {value!r} is not one of {', '.join(PROFILES)}",
            field="profile",
            unlock="pass --profile economy|balanced|deep",
        )
    return value


def manifest_profile(root: Path) -> EconomyProfile | None:
    path = Path(root) / ".apiforge" / "project.yaml"
    if not path.is_file():
        return None
    from apiforge.workspace.manifests import load_project_manifest

    try:
        return load_project_manifest(path).economy_profile
    except (ContractError, OSError, ValueError):
        return None


def resolve_profile(
    flag: str | None, manifest: str | None, config: Mapping[str, Any]
) -> tuple[EconomyProfile, ProfileSource]:
    requested = validate_profile(flag)
    if requested is not None:
        return requested, "flag"
    from_manifest = validate_profile(manifest)
    if from_manifest is not None:
        return from_manifest, "manifest"
    default = validate_profile(str(config.get("default_profile", "balanced")))
    return cast(EconomyProfile, default), "policy"


def risk_floor(
    decision: RoutingDecision, task_risk: str, config: Mapping[str, Any]
) -> tuple[EconomyProfile, str | None]:
    risk = decision.risk_complexity
    graph = decision.graph_impact
    complexity = risk.complexity if risk is not None else None
    gates = {
        item
        for item in (risk.gate_state if risk else None, graph.gate_state if graph else None)
        if item
    }
    floors = config.get("floors", {})
    for profile in ("deep", "balanced"):
        rule = floors.get(profile, {})
        reasons = []
        if complexity in rule.get("complexity", ()):
            reasons.append(f"complexity={complexity}")
        if task_risk in rule.get("risk", ()):
            reasons.append(f"risk={task_risk}")
        hit_gates = sorted(gates & set(rule.get("gate", ())))
        if hit_gates:
            reasons.append(f"gate={','.join(hit_gates)}")
        if reasons:
            return profile, "; ".join(reasons)
    return "economy", None


def envelope_for(profile: EconomyProfile, config: Mapping[str, Any]) -> BudgetEnvelope:
    return BudgetEnvelope(profile=profile, **config["profiles"][profile])


def build_economy_plan(
    decision: RoutingDecision,
    spec: TaskSpec,
    *,
    flag: str | None,
    manifest: str | None,
    config: Mapping[str, Any] | None = None,
) -> EconomyPlan:
    selected = config or load_economy_config()
    requested, source = resolve_profile(flag, manifest, selected)
    floor, reason = risk_floor(decision, spec.risk.value, selected)
    effective = PROFILES[max(PROFILES.index(requested), PROFILES.index(floor))]
    escalated = PROFILES.index(effective) > PROFILES.index(requested)
    minimum = (
        tuple(sorted(decision.risk_complexity.required_roles)) if decision.risk_complexity else ()
    )
    if decision.graph_impact is not None:
        minimum = tuple(sorted({*minimum, *decision.graph_impact.required_roles}))
    return EconomyPlan(
        requested=requested,
        requested_source=source,
        floor=floor,
        effective=effective,
        escalation_reason=reason if escalated else None,
        envelope=envelope_for(effective, selected),
        minimum_roles=minimum,
        diagnostics=(f"{ESCALATED}: {requested}->{effective} ({reason})",) if escalated else (),
    )


def role_kinds(plan: RoutingPlan, kinds: Mapping[str, str]) -> set[str]:
    names = [*plan.reviewers, plan.critic, plan.referee]
    return {kinds[name] for name in names if name is not None and name in kinds}


def apply_economy(
    plan: RoutingPlan,
    economy: EconomyPlan,
    decision: RoutingDecision,
    kinds: Mapping[str, str],
) -> tuple[RoutingPlan, EconomyPlan]:
    envelope = economy.envelope
    parallel = plan.parallel[: envelope.fanout]
    fallbacks = plan.fallbacks[: envelope.fallbacks]
    challengers = plan.challenger_order[: envelope.challenger_slots]
    trimmed = tuple(
        sorted(
            (set(plan.parallel) - set(parallel))
            | (set(plan.fallbacks) - set(fallbacks))
            | (set(plan.challenger_order) - set(challengers))
        )
    )
    kept = plan.model_copy(
        update={
            "parallel": parallel,
            "fallbacks": fallbacks,
            "max_fallbacks": min(plan.max_fallbacks, envelope.fallbacks),
            "challenger_order": challengers,
            "challenger_slots": min(plan.challenger_slots, envelope.challenger_slots),
        }
    )
    if role_kinds(kept, kinds) != role_kinds(plan, kinds):
        raise ContractError(
            "AF-ECONOMY-ROLE-INVARIANT",
            "economy trim changed the reviewer/critic/referee roles required by risk",
        )
    used = {
        name
        for name in (
            kept.primary,
            *kept.parallel,
            *kept.reviewers,
            kept.critic,
            kept.referee,
            *kept.fallbacks,
        )
        if name
    }
    escalation = next(
        (
            name
            for name in decision.fallback_order
            if kinds.get(name) == "reviewer" and name not in used
        ),
        None,
    )
    return kept, economy.model_copy(
        update={"trimmed_roles": trimmed, "escalation_reviewer": escalation}
    )


def reserve_calls(envelope: BudgetEnvelope, max_calls: int) -> int:
    return min(max_calls, math.ceil(max_calls * envelope.verification_share))


def allows(economy: EconomyPlan, level: LadderLevel) -> bool:
    return LEVELS.index(level) <= LEVELS.index(economy.envelope.ladder_ceiling)


def needs_escalation(
    confidences: Sequence[float],
    unresolved: Sequence[str],
    recommendations: Sequence[str],
    threshold: float,
) -> tuple[str, ...]:
    triggers: list[str] = []
    if confidences and min(confidences) < threshold:
        triggers.append("low_confidence")
    if unresolved:
        triggers.append("unresolved")
    if len(set(recommendations)) > 1:
        triggers.append("conflict")
    return tuple(triggers)


def deterministic_proof(root: Path, spec: TaskSpec) -> DeterministicProof:
    expected = tuple(spec.expected_proofs)
    runs_dir = Path(root) / ".apiforge" / "tasks" / spec.id / "runs"
    if not expected or not runs_dir.is_dir():
        return DeterministicProof(None, (), expected)
    for path in sorted(
        runs_dir.glob("*.json"),
        key=lambda item: int(item.stem) if item.stem.isdigit() else -1,
        reverse=True,
    ):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(payload, dict) or "steps" not in payload or "run_id" in payload:
            continue
        steps = [item for item in payload.get("steps") or [] if isinstance(item, dict)]
        ran = [json.dumps(item, sort_keys=True) for item in steps if item.get("status") == "ran"]
        found = tuple(item for item in expected if any(item in text for text in ran))
        missing = tuple(item for item in expected if item not in found)
        complete = (
            bool(steps)
            and len(ran) == len(steps)
            and payload.get("terminal") == "awaiting_supervision"
        )
        level: LadderLevel | None = "L0" if complete and not missing else "L1" if found else None
        return DeterministicProof(level, found, missing, path.name)
    return DeterministicProof(None, (), expected)


__all__ = [
    "LEVELS",
    "PROFILES",
    "DeterministicProof",
    "EconomyError",
    "allows",
    "apply_economy",
    "build_economy_plan",
    "deterministic_proof",
    "envelope_for",
    "load_economy_config",
    "manifest_profile",
    "needs_escalation",
    "reserve_calls",
    "resolve_profile",
    "risk_floor",
    "validate_profile",
]
