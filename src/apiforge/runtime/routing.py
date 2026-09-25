"""Deterministic capability eligibility, ranking and replay traces."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import yaml

from apiforge.contracts.agentic import AgentCapabilityProfile, AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.contracts.graph import GraphEdge, GraphExport, GraphNode
from apiforge.contracts.graph_impact import GraphImpactAssessment
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
from apiforge.graph.impact import assess_graph_impact
from apiforge.runtime.registry import Capability, select_capabilities
from apiforge.runtime.risk_complexity import assess_risk_complexity
from apiforge.runtime.scorecard_routing import assess_scorecard_routing
from apiforge.runtime.scorecard_shadow import evaluate_scorecard_shadow


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
        values: dict[str, object] = {
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
        if raw.get("risk_complexity") is not None:
            values["risk_complexity"] = raw["risk_complexity"]
        if raw.get("scorecard_adaptation") is not None:
            values["scorecard_adaptation"] = raw["scorecard_adaptation"]
        if raw.get("graph_impact") is not None:
            values["graph_impact"] = raw["graph_impact"]
        return RoutingPolicy.model_validate(values)
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError("AF-RUNTIME-POLICY", f"invalid runtime.routing: {exc}") from exc


def build_routing_request(
    spec: TaskSpec,
    *,
    policy_id: str,
    available_evidence: tuple[str, ...] = (),
    required_expertise: tuple[str, ...] = (),
    available_expertise: tuple[str, ...] = (),
    graph_target: str | None = None,
    graph_mode: str | None = None,
    graph_candidate_refs: Mapping[str, Sequence[str]] | None = None,
    graph_freshness_state: str | None = None,
    graph_evidence: tuple[str, ...] = (),
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
        required_expertise=required_expertise,
        available_expertise=available_expertise,
        inputs=spec.inputs,
        task_size=spec.size.value,
        dependencies=spec.dependencies,
        expected_proofs=spec.expected_proofs,
        strategy=spec.strategy.value,
        policy_id=policy_id,
        graph_target=graph_target,
        graph_mode=graph_mode,  # type: ignore[arg-type]
        graph_candidate_refs={
            str(name): tuple(sorted({str(ref) for ref in refs}))
            for name, refs in sorted((graph_candidate_refs or {}).items())
        },
        graph_freshness_state=graph_freshness_state,  # type: ignore[arg-type]
        graph_evidence=tuple(sorted(set(graph_evidence))),
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
    required_packs = (
        set(profile.expertise_packs)
        | set(capability.expertise_packs)
        | set(request.required_expertise)
    )
    missing_packs = tuple(sorted(required_packs.difference(request.available_expertise)))
    if missing_packs:
        return _rejection(
            f"missing expertise packs: {', '.join(missing_packs)}",
            field="capability.expertise_packs",
            unlock="make the validated local expertise pack available before routing",
        )
    return None


def _scorecard_map(scorecards: Sequence[AgentScorecard]) -> dict[str, AgentScorecard]:
    values: dict[str, AgentScorecard] = {}
    for scorecard in sorted(scorecards, key=lambda item: item.model_dump_json()):
        values[scorecard.profile_id] = scorecard
        values[scorecard.agent] = scorecard
    return values


def signals_from_scorecards(
    scorecards: Sequence[AgentScorecard],
) -> dict[str, tuple[ObservedSignal, ...]]:
    result: dict[str, tuple[ObservedSignal, ...]] = {}
    for scorecard in sorted(scorecards, key=lambda item: item.model_dump_json()):
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
                    freshness_state=scorecard.freshness_state,
                    observed_at=scorecard.observed_at,
                    expires_at=scorecard.expires_at,
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
                    freshness_state=scorecard.freshness_state,
                    observed_at=scorecard.observed_at,
                    expires_at=scorecard.expires_at,
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
                    freshness_state=scorecard.freshness_state,
                    observed_at=scorecard.observed_at,
                    expires_at=scorecard.expires_at,
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
    additional_capabilities: tuple[str, ...] = (),
) -> tuple[CandidateAssessment, ...]:
    assessments: list[CandidateAssessment] = []
    for capability in select_capabilities(
        dict(capabilities),
        requested=request.requested_capabilities,
        risk=request.risk,
        additional_names=additional_capabilities,
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
        if signal.name == name
        and signal.status == "observed"
        and signal.freshness_state not in {"stale", "unresolved"}
        and signal.value is not None
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


def _graph_selection_rank(effect: str) -> int:
    return {"prefer": 0, "neutral": 1, "unresolved": 1, "demote": 2, "exclude": 3}.get(effect, 1)


def apply_graph_selection(
    assessments: Sequence[CandidateAssessment],
    graph_impact: GraphImpactAssessment | None,
) -> tuple[CandidateAssessment, ...]:
    """Apply only explicit graph preferences while preserving static fallback order."""
    if graph_impact is None:
        return tuple(assessments)
    effects = {item.candidate: item.selection for item in graph_impact.candidate_impacts}
    return tuple(
        sorted(
            assessments,
            key=lambda item: (
                _graph_selection_rank(effects.get(item.capability, "unresolved")),
                item.ranking_key,
            ),
        )
    )


def _graph_assessment(
    request: RoutingRequest,
    policy: RoutingPolicy,
    *,
    graph_nodes: Sequence[GraphNode],
    graph_edges: Sequence[GraphEdge],
    graph_snapshot: GraphExport | None,
) -> GraphImpactAssessment | None:
    if request.graph_target is None:
        return None
    return assess_graph_impact(
        graph_nodes,
        graph_edges,
        request.graph_target,
        mode=request.graph_mode,
        policy=policy.graph_impact,
        graph_snapshot=graph_snapshot,
        freshness_state=request.graph_freshness_state or "fresh",
        candidate_refs=request.graph_candidate_refs,
        evidence=request.graph_evidence,
    )


def _role_capabilities(
    capabilities: Mapping[str, Capability], roles: tuple[str, ...]
) -> tuple[str, ...]:
    required_kinds = set(roles)
    return tuple(sorted(item.name for item in capabilities.values() if item.kind in required_kinds))


def route_capabilities(
    capabilities: Mapping[str, Capability],
    profiles: Mapping[str, AgentCapabilityProfile],
    request: RoutingRequest,
    *,
    policy: RoutingPolicy | None = None,
    scorecards: Sequence[AgentScorecard] = (),
    signals: Mapping[str, tuple[ObservedSignal, ...]] | None = None,
    graph_nodes: Sequence[GraphNode] = (),
    graph_edges: Sequence[GraphEdge] = (),
    graph_snapshot: GraphExport | None = None,
) -> RoutingDecision:
    selected_policy = policy or load_routing_policy()
    assessment = assess_risk_complexity(request, selected_policy)
    graph_impact = _graph_assessment(
        request,
        selected_policy,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        graph_snapshot=graph_snapshot,
    )
    required_roles = tuple(
        sorted(
            {
                *assessment.required_roles,
                *(graph_impact.required_roles if graph_impact is not None else ()),
            }
        )
    )
    scorecard_values = _scorecard_map(scorecards)
    supplied_signals = signals or signals_from_scorecards(scorecards)
    assessments = assess_candidates(
        capabilities,
        profiles,
        request,
        signals=supplied_signals,
        additional_capabilities=_role_capabilities(
            capabilities,
            required_roles,
        ),
    )
    ranking_policy = selected_policy.model_copy(
        update={"objective_order": assessment.objective_order}
    )
    ranked_candidates = rank_eligible(
        assessments,
        scorecards=scorecard_values,
        policy=ranking_policy,
    )
    ranked_candidates = apply_graph_selection(ranked_candidates, graph_impact)
    scorecard_routing = assess_scorecard_routing(
        ranked_candidates,
        scorecard_values,
        selected_policy.scorecard_adaptation,
    )
    ranked_by_name = {item.capability: item for item in ranked_candidates}
    adaptive_candidates = tuple(
        ranked_by_name[name]
        for name in scorecard_routing.ordered_candidates
        if name in ranked_by_name
    )
    role_names = set(_role_capabilities(capabilities, required_roles))
    baseline_order = tuple(
        item.capability
        for group in (
            tuple(item for item in ranked_candidates if item.capability not in role_names),
            tuple(item for item in ranked_candidates if item.capability in role_names),
        )
        for item in group
    )
    ranked = tuple(
        item
        for group in (
            tuple(item for item in adaptive_candidates if item.capability not in role_names),
            tuple(item for item in adaptive_candidates if item.capability in role_names),
        )
        for item in group
    )
    ordered = tuple(item.capability for item in ranked)
    shadow_evaluation = evaluate_scorecard_shadow(
        assessment=scorecard_routing,
        baseline_policy_version=selected_policy.policy_version,
        baseline_order=baseline_order,
        adaptive_order=ordered,
        baseline_selected=baseline_order[0] if baseline_order else None,
        adaptive_selected=ordered[0] if ordered else None,
    )
    unresolved = [
        f"{item.capability}:{signal.name}:unresolved"
        for item in assessments
        for signal in item.signals
        if signal.status != "observed" and signal.name in {"cost", "duration", "quality"}
    ]
    unresolved.extend(assessment.unresolved)
    if graph_impact is not None:
        unresolved.extend(graph_impact.unresolved)
    unresolved.extend(scorecard_routing.unresolved)
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
        "assessment": assessment.model_dump(mode="json"),
        "graph_impact": (
            graph_impact.model_dump(mode="json") if graph_impact is not None else None
        ),
        "scorecard_routing": scorecard_routing.model_dump(mode="json"),
        "shadow_evaluation": shadow_evaluation.model_dump(mode="json"),
        "candidates": [item.model_dump(mode="json") for item in candidate_trace],
    }
    decision_id = stable_id("routing", decision_payload)
    return RoutingDecision(
        decision_id=decision_id,
        task_id=request.task_id,
        revision=request.revision,
        policy_id=selected_policy.policy_id,
        candidates=candidate_trace,
        selected=ordered[0] if ordered else None,
        fallback_order=ordered,
        risk_complexity=assessment,
        graph_impact=graph_impact,
        scorecard_routing=scorecard_routing,
        shadow_evaluation=shadow_evaluation,
        evidence=tuple(
            sorted(
                {
                    *request.available_evidence,
                    *scorecard_routing.evidence,
                    *(graph_impact.evidence if graph_impact is not None else ()),
                    *(
                        (f"graph-impact:{graph_impact.assessment_id}",)
                        if graph_impact is not None
                        else ()
                    ),
                }
            )
        ),
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
    risk_assessment = decision.risk_complexity
    graph_assessment = decision.graph_impact
    required_roles = (
        tuple(
            sorted(
                {
                    *(risk_assessment.required_roles if risk_assessment is not None else ()),
                    *(graph_assessment.required_roles if graph_assessment is not None else ()),
                }
            )
        )
        if risk_assessment is not None
        else tuple(
            sorted(
                {
                    "reviewer",
                    "critic",
                    "referee",
                    *(graph_assessment.required_roles if graph_assessment is not None else ()),
                }
            )
        )
    )
    role_kinds = {"reviewer", "critic", "referee"}
    primary_candidates = tuple(
        name for name in ordered if capabilities[name].kind not in role_kinds | {"fallback"}
    )
    primary = (
        decision.selected
        if decision.selected in primary_candidates
        else primary_candidates[0]
        if primary_candidates
        else None
    )
    remaining = tuple(name for name in ordered if name != primary)
    reviewers = tuple(
        name
        for name in remaining
        if capabilities[name].kind == "reviewer" and "reviewer" in required_roles
    )
    critic = next(
        (
            name
            for name in remaining
            if capabilities[name].kind == "critic" and "critic" in required_roles
        ),
        None,
    )
    referee = next(
        (
            name
            for name in remaining
            if capabilities[name].kind == "referee" and "referee" in required_roles
        ),
        None,
    )
    explicit_fallbacks = tuple(name for name in remaining if capabilities[name].kind == "fallback")
    specialists = tuple(
        name
        for name in remaining
        if capabilities[name].kind not in role_kinds and name not in explicit_fallbacks
    )
    if selected_policy.execution_mode == "sequential_failover":
        fallbacks = (*explicit_fallbacks, *specialists)[: selected_policy.max_fallbacks]
        parallel: tuple[str, ...] = ()
    else:
        fallbacks = explicit_fallbacks[: selected_policy.max_fallbacks]
        parallel = tuple(name for name in specialists if name not in fallbacks)
    missing_roles = []
    if "reviewer" in required_roles and not reviewers:
        missing_roles.append(
            "AF-CAPABILITY-ELIGIBILITY: field=routing_plan.reviewers; "
            "unlock=provide an eligible reviewer capability"
        )
    if "critic" in required_roles and critic is None:
        missing_roles.append(
            "AF-CAPABILITY-ELIGIBILITY: field=routing_plan.critic; "
            "unlock=provide an eligible critic capability"
        )
    if "referee" in required_roles and referee is None:
        missing_roles.append(
            "AF-CAPABILITY-ELIGIBILITY: field=routing_plan.referee; "
            "unlock=provide an eligible referee capability"
        )
    unresolved = tuple(sorted({*decision.unresolved, *missing_roles}))
    gate_unresolved = tuple(
        sorted(
            {
                *(risk_assessment.unresolved if risk_assessment is not None else ()),
                *missing_roles,
                *(
                    ("graph-impact:blocked-by-policy",)
                    if graph_assessment is not None and graph_assessment.gate_state == "blocked"
                    else ()
                ),
            }
        )
    )
    gate_states = [
        risk_assessment.gate_state if risk_assessment is not None else "open",
        graph_assessment.gate_state if graph_assessment is not None else "open",
        "blocked" if gate_unresolved else "open",
    ]
    gate_state = max(gate_states, key=lambda value: {"open": 0, "review": 1, "blocked": 2}[value])
    depth_states = [
        risk_assessment.verification_depth if risk_assessment is not None else "standard",
        graph_assessment.verification_depth if graph_assessment is not None else "standard",
    ]
    verification_depth = max(
        depth_states,
        key=lambda value: {"standard": 0, "elevated": 1, "strict": 2}[value],
    )
    scorecard_assessment = decision.scorecard_routing
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
        "assessment_id": risk_assessment.assessment_id if risk_assessment is not None else None,
        "graph_impact": (
            graph_assessment.model_dump(mode="json") if graph_assessment is not None else None
        ),
        "complexity": risk_assessment.complexity if risk_assessment is not None else None,
        "verification_depth": verification_depth,
        "required_roles": required_roles,
        "gate_state": gate_state,
        "challenger_order": (
            scorecard_assessment.selected_challengers if scorecard_assessment is not None else ()
        ),
        "challenger_slots": (
            scorecard_assessment.challenger_slots if scorecard_assessment is not None else 0
        ),
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
        assessment_id=risk_assessment.assessment_id if risk_assessment is not None else None,
        graph_impact=graph_assessment,
        complexity=risk_assessment.complexity if risk_assessment is not None else None,
        verification_depth=verification_depth,
        required_roles=required_roles,
        gate_state=gate_state,
        challenger_order=(
            decision.scorecard_routing.selected_challengers
            if decision.scorecard_routing is not None
            else ()
        ),
        challenger_slots=(
            decision.scorecard_routing.challenger_slots
            if decision.scorecard_routing is not None
            else 0
        ),
        evidence=decision.evidence,
        unresolved=unresolved,
    )
