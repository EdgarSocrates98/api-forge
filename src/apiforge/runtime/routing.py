"""Deterministic capability eligibility, ranking and replay traces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml

from apiforge.contracts.agentic import AgentCapabilityProfile, AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.contracts.routing import (
    CandidateAssessment,
    ObservedSignal,
    RoutingDecision,
    RoutingPlan,
    RoutingPolicy,
    RoutingRequest,
)
from apiforge.contracts.task import TaskSpec
from apiforge.core.ids import stable_id
from apiforge.runtime.registry import Capability, select_capabilities


def _routing_path() -> Path:
    return Path(__file__).resolve().parents[1] / "rules" / "agentic_runtime.yaml"


def load_routing_policy(path: Path | None = None) -> RoutingPolicy:
    source = path or _routing_path()
    try:
        document = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ContractError("AF-RUNTIME-POLICY", str(exc)) from exc
    raw = document.get("runtime", {}).get("routing") if isinstance(document, dict) else None
    if not isinstance(raw, dict):
        raise ContractError("AF-RUNTIME-POLICY", "missing runtime.routing")
    try:
        policy_version = str(raw["policy_version"])
        return RoutingPolicy.model_validate(
            {
                "policy_id": policy_version,
                "policy_version": policy_version,
                "objective_order": tuple(str(item) for item in raw.get("objective_order", ())),
                "security_mode": str(raw.get("security_mode", "gate")),
                "unknown_signal": str(raw.get("unknown_signal", "unresolved")),
                "tie_breaker": str(raw.get("tie_breaker", "capability")),
                "scorecard_update": str(raw.get("scorecard_update", "eval_required")),
                "execution_mode": str(raw.get("execution_mode", "parallel_review")),
                "max_fallbacks": int(raw.get("max_fallbacks", 1)),
            }
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError("AF-RUNTIME-POLICY", f"invalid runtime.routing: {exc}") from exc


def build_routing_request(
    spec: TaskSpec,
    *,
    policy_id: str,
    available_evidence: tuple[str, ...] = (),
) -> RoutingRequest:
    requested = (spec.capability_covered,) if spec.capability_covered else ()
    evidence = tuple(sorted({"task_spec", *available_evidence}))
    return RoutingRequest(
        task_id=spec.id,
        revision=spec.revision,
        risk=spec.risk.value,
        requested_capabilities=requested,
        required_evidence=spec.preconditions,
        available_evidence=evidence,
        inputs=spec.inputs,
        policy_id=policy_id,
    )


def available_routing_evidence(decision: RoutingDecision) -> tuple[str, ...]:
    """Return deterministic evidence references available after routing."""
    return tuple(sorted({"routing_decision", *decision.evidence, "task_spec"}))


def _rejection(detail: str, *, field: str, unlock: str) -> dict[str, str]:
    return {
        "code": "AF-CAPABILITY-ELIGIBILITY",
        "detail": detail,
        "field": field,
        "unlock": unlock,
    }


def check_eligibility(
    capability: Capability,
    profiles: Mapping[str, AgentCapabilityProfile],
    request: RoutingRequest,
) -> dict[str, str] | None:
    profile = profiles.get(capability.name)
    if profile is None:
        return _rejection(
            "capability profile is missing",
            field="profile",
            unlock="provide the versioned local profile registry entry",
        )
    if not profile.enabled:
        return _rejection(
            "capability profile is disabled",
            field="profile.enabled",
            unlock="enable the capability only after reviewing its policy",
        )
    if capability.state in {"unsupported", "unresolved"}:
        return _rejection(
            f"capability state is {capability.state}",
            field="capability.state",
            unlock="use a supported capability or resolve its runtime evidence",
        )
    if request.risk not in profile.accepted_risks:
        return _rejection(
            f"risk {request.risk!r} is not accepted by the profile",
            field="profile.accepted_risks",
            unlock="choose a profile with an explicit accepted risk",
        )
    required = set(profile.required_evidence) | set(capability.prerequisites)
    required.update(request.required_evidence)
    missing = tuple(sorted(required.difference(request.available_evidence)))
    if missing:
        return _rejection(
            f"missing evidence or prerequisites: {', '.join(missing)}",
            field="capability.evidence",
            unlock="provide the missing evidence before routing",
        )
    return None


def _scorecard_map(scorecards: Sequence[AgentScorecard]) -> dict[str, AgentScorecard]:
    values: dict[str, AgentScorecard] = {}
    for scorecard in scorecards:
        values[scorecard.profile_id] = scorecard
        values[scorecard.agent] = scorecard
    return values


def signals_from_scorecards(
    scorecards: Sequence[AgentScorecard],
) -> dict[str, tuple[ObservedSignal, ...]]:
    result: dict[str, tuple[ObservedSignal, ...]] = {}
    for scorecard in scorecards:
        signals: list[ObservedSignal] = []
        if scorecard.observed_cost is not None:
            signals.append(
                ObservedSignal(
                    name="cost",
                    value=scorecard.observed_cost,
                    status="observed",
                    unit="cost",
                    source="scorecard",
                    evidence_refs=scorecard.observation_refs,
                )
            )
        if scorecard.observed_duration_ms is not None:
            signals.append(
                ObservedSignal(
                    name="duration",
                    value=scorecard.observed_duration_ms,
                    status="observed",
                    unit="ms",
                    source="scorecard",
                    evidence_refs=scorecard.observation_refs,
                )
            )
        if scorecard.quality_promoted and scorecard.evaluation_count:
            signals.append(
                ObservedSignal(
                    name="quality",
                    value=scorecard.quality_score,
                    status="observed",
                    unit="score",
                    source="scorecard",
                    evidence_refs=scorecard.computed_from,
                )
            )
        result[scorecard.profile_id] = tuple(signals)
    return result


def _signals_for(
    capability: str,
    provided: Mapping[str, tuple[ObservedSignal, ...]],
) -> tuple[ObservedSignal, ...]:
    existing = {signal.name: signal for signal in provided.get(capability, ())}
    for name in ("cost", "duration", "quality"):
        existing.setdefault(name, ObservedSignal(name=name, status="unknown"))
    return tuple(existing[name] for name in sorted(existing))


def assess_candidates(
    capabilities: Mapping[str, Capability],
    profiles: Mapping[str, AgentCapabilityProfile],
    request: RoutingRequest,
    *,
    signals: Mapping[str, tuple[ObservedSignal, ...]] | None = None,
) -> tuple[CandidateAssessment, ...]:
    assessments: list[CandidateAssessment] = []
    for capability in select_capabilities(
        dict(capabilities),
        requested=request.requested_capabilities,
        risk=request.risk,
    ):
        rejection = check_eligibility(capability, profiles, request)
        assessments.append(
            CandidateAssessment(
                capability=capability.name,
                agent=capability.agent,
                eligible=rejection is None,
                rejection=rejection,
                signals=_signals_for(capability.name, signals or {}),
                family=capability.family,
                implementation=capability.implementation,
                expertise_packs=capability.expertise_packs,
            )
        )
    return tuple(assessments)


def _observed_value(assessment: CandidateAssessment, name: str) -> float | None:
    values = [
        signal.value
        for signal in assessment.signals
        if signal.name == name and signal.status == "observed" and signal.value is not None
    ]
    if not values:
        return None
    return max(values) if name == "quality" else min(values)


def ranking_key(
    assessment: CandidateAssessment,
    scorecards: Mapping[str, AgentScorecard],
    policy: RoutingPolicy,
) -> tuple[str, ...]:
    parts: list[str] = []
    scorecard = scorecards.get(assessment.capability) or scorecards.get(assessment.agent)
    for objective in policy.objective_order:
        if objective == "efficiency":
            duration = _observed_value(assessment, "duration")
            cost = _observed_value(assessment, "cost")
            parts.extend(
                (
                    "0" if duration is not None or cost is not None else "1",
                    "0" if duration is not None else "1",
                    f"{duration:.9f}" if duration is not None else "unknown",
                    "0" if cost is not None else "1",
                    f"{cost:.9f}" if cost is not None else "unknown",
                )
            )
        elif objective == "quality":
            scorecard_quality = (
                scorecard.quality_score
                if scorecard is not None
                and scorecard.evaluation_count
                and (
                    scorecard.quality_promoted
                    or (scorecard.computed_from and scorecard.quality_score > 0)
                )
                else None
            )
            quality = (
                scorecard_quality
                if scorecard_quality is not None
                else _observed_value(assessment, "quality")
            )
            parts.extend(
                (
                    "0" if quality is not None else "1",
                    f"{1 - quality:.9f}" if quality is not None else "unknown",
                )
            )
    if policy.tie_breaker == "capability":
        parts.append(assessment.capability)
    return tuple(parts)


def rank_eligible(
    assessments: Sequence[CandidateAssessment],
    *,
    scorecards: Mapping[str, AgentScorecard],
    policy: RoutingPolicy,
) -> tuple[CandidateAssessment, ...]:
    ranked: list[CandidateAssessment] = []
    for assessment in assessments:
        if assessment.eligible:
            ranked.append(
                assessment.model_copy(
                    update={"ranking_key": ranking_key(assessment, scorecards, policy)}
                )
            )
    return tuple(sorted(ranked, key=lambda item: item.ranking_key))


def route_capabilities(
    capabilities: Mapping[str, Capability],
    profiles: Mapping[str, AgentCapabilityProfile],
    request: RoutingRequest,
    *,
    policy: RoutingPolicy | None = None,
    scorecards: Sequence[AgentScorecard] = (),
    signals: Mapping[str, tuple[ObservedSignal, ...]] | None = None,
) -> RoutingDecision:
    selected_policy = policy or load_routing_policy()
    scorecard_values = _scorecard_map(scorecards)
    supplied_signals = signals or signals_from_scorecards(scorecards)
    assessments = assess_candidates(
        capabilities,
        profiles,
        request,
        signals=supplied_signals,
    )
    ranked = rank_eligible(
        assessments,
        scorecards=scorecard_values,
        policy=selected_policy,
    )
    unresolved = [
        f"{item.capability}:{signal.name}:unresolved"
        for item in ranked
        for signal in item.signals
        if signal.status != "observed" and signal.name in {"cost", "duration", "quality"}
    ]
    if not ranked:
        unresolved.append(
            "AF-CAPABILITY-ELIGIBILITY: field=capability; unlock=provide eligible evidence"
        )
    candidate_trace = tuple(
        next(
            (item for item in ranked if item.capability == assessment.capability),
            assessment,
        )
        for assessment in assessments
    )
    decision_payload = {
        "task_id": request.task_id,
        "revision": request.revision,
        "policy": selected_policy.model_dump(mode="json"),
        "candidates": [item.model_dump(mode="json") for item in candidate_trace],
    }
    decision_id = stable_id("routing", decision_payload)
    ordered = tuple(item.capability for item in ranked)
    return RoutingDecision(
        decision_id=decision_id,
        task_id=request.task_id,
        revision=request.revision,
        policy_id=selected_policy.policy_id,
        candidates=candidate_trace,
        selected=ordered[0] if ordered else None,
        fallback_order=ordered,
        evidence=tuple(sorted(request.available_evidence)),
        unresolved=tuple(sorted(set(unresolved))),
    )


def build_routing_plan(
    decision: RoutingDecision,
    capabilities: Mapping[str, Capability],
    *,
    policy: RoutingPolicy | None = None,
) -> RoutingPlan:
    """Convert ranked candidates into explicit, stable execution roles."""
    selected_policy = policy or load_routing_policy()
    ordered = tuple(name for name in decision.fallback_order if name in capabilities)
    primary = decision.selected if decision.selected in capabilities else None
    remaining = tuple(name for name in ordered if name != primary)
    reviewers = tuple(name for name in remaining if capabilities[name].kind == "reviewer")
    critic = next(
        (name for name in remaining if capabilities[name].kind == "critic"),
        None,
    )
    referee = next(
        (name for name in remaining if capabilities[name].kind == "referee"),
        None,
    )
    role_names = set(reviewers) | {name for name in (critic, referee) if name is not None}
    explicit_fallbacks = tuple(name for name in remaining if capabilities[name].kind == "fallback")
    specialists = tuple(
        name
        for name in remaining
        if name not in role_names and name not in explicit_fallbacks
    )
    if selected_policy.execution_mode == "sequential_failover":
        fallbacks = (*explicit_fallbacks, *specialists)[: selected_policy.max_fallbacks]
        parallel: tuple[str, ...] = ()
    else:
        fallbacks = explicit_fallbacks[: selected_policy.max_fallbacks]
        parallel = tuple(name for name in specialists if name not in fallbacks)
    payload = {
        "decision_id": decision.decision_id,
        "task_id": decision.task_id,
        "revision": decision.revision,
        "primary": primary,
        "fallbacks": fallbacks,
        "parallel": parallel,
        "reviewers": reviewers,
        "critic": critic,
        "referee": referee,
        "execution_mode": selected_policy.execution_mode,
        "max_fallbacks": selected_policy.max_fallbacks,
    }
    return RoutingPlan(
        plan_id=stable_id("routing-plan", payload),
        decision_id=decision.decision_id,
        task_id=decision.task_id,
        revision=decision.revision,
        primary=primary,
        fallbacks=fallbacks,
        parallel=parallel,
        reviewers=reviewers,
        critic=critic,
        referee=referee,
        execution_mode=selected_policy.execution_mode,
        max_fallbacks=selected_policy.max_fallbacks,
        evidence=decision.evidence,
        unresolved=decision.unresolved,
    )
