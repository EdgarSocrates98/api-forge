"""Deterministic supervisor for one TaskSpec-bound agentic run."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from pydantic import TypeAdapter

from apiforge.capabilities.scorecard import load_scorecards
from apiforge.contracts.agentic import (
    AgentArtifact,
    AgenticRun,
    AgenticState,
    AgentInvocation,
    ArtifactKind,
    TrajectoryEvent,
)
from apiforge.contracts.agentic_governance import (
    GovernorInputs,
    LoopAction,
    LoopDetection,
    RecoveryDecision,
    RunGovernanceContext,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import EconomyPlan, LadderStep
from apiforge.contracts.graph import GraphEdge, GraphExport, GraphNode
from apiforge.contracts.routing import RoutingDecision
from apiforge.contracts.routing_evolution import PromotionGate
from apiforge.contracts.selective import RoleContext, RoleContextPlan, ShadowDecision
from apiforge.core.ids import stable_id
from apiforge.core.models import JsonValue
from apiforge.governance.gain import expected_gain
from apiforge.governance.governor import govern
from apiforge.governance.loop import check_loop, load_loop_policy, strategy_fingerprint
from apiforge.governance.recovery import classify_failure, decide_recovery
from apiforge.governance.stop import decide_stop
from apiforge.graph.store import read_graph
from apiforge.runtime.adapters import AgentRequest, ModelAdapter
from apiforge.runtime.control import ControlPlane
from apiforge.runtime.critic import critic_findings
from apiforge.runtime.economy import (
    DeterministicProof,
    allows,
    apply_economy,
    build_economy_plan,
    deterministic_proof,
    load_economy_config,
    manifest_profile,
    needs_escalation,
    reserve_calls,
    validate_profile,
)
from apiforge.runtime.economy_checkpoint import (
    build_checkpoint,
    load_checkpoint,
    pin_profile,
    save_checkpoint,
)
from apiforge.runtime.guardrails import validate_agent_payload
from apiforge.runtime.information_gain import assess as assess_gain
from apiforge.runtime.policy import (
    load_policy,
    requires_critic,
    requires_human_gate,
    should_open_room,
)
from apiforge.runtime.promotion import decide_promotion, is_active, load_evolution_policy
from apiforge.runtime.registry import load_capabilities, load_profiles
from apiforge.runtime.review import build_runtime_review, review_task_spec
from apiforge.runtime.role_context import plan_roles
from apiforge.runtime.role_context import record as record_roles
from apiforge.runtime.role_context import summary as role_summary
from apiforge.runtime.routing import (
    available_routing_evidence,
    build_routing_plan,
    build_routing_request,
    load_routing_policy,
    route_capabilities,
)
from apiforge.runtime.scheduler import run_bounded
from apiforge.runtime.shadow import decide as decide_shadow
from apiforge.runtime.store import RunStore, content_hash
from apiforge.taskspec import store as task_store
from apiforge.trust.tools import authorize, load_tool_risk


def _now(value: str | None) -> str:
    return value or datetime.now(UTC).isoformat()


def _run_id(task_id: str, revision: int, now: str) -> str:
    return stable_id("run", {"task_id": task_id, "revision": revision, "started_at": now})


def _artifact_payload(response: object) -> dict[str, object]:
    if not hasattr(response, "output"):
        raise ContractError("AF-RUNTIME-SCHEMA", "adapter response has no structured output")
    output = response.output
    if not isinstance(output, dict):
        raise ContractError("AF-RUNTIME-SCHEMA", "adapter output must be an object")
    return dict(output)


def _json_payload(response: object) -> dict[str, JsonValue]:
    return TypeAdapter(dict[str, JsonValue]).validate_python(_artifact_payload(response))


def _strings(payload: dict[str, JsonValue], key: str) -> tuple[str, ...]:
    value = payload.get(key, ())
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def _confidence(payload: dict[str, JsonValue]) -> float | None:
    value = payload.get("confidence")
    return float(value) if isinstance(value, (int, float)) else None


def _recommendation(artifact: AgentArtifact) -> str:
    payload = artifact.payload
    if isinstance(payload, dict):
        return str(payload.get("recommendation", ""))
    return ""


def _input_paths(spec: Any) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for item in spec.inputs:
        key, sep, value = item.partition("=")
        if sep and key in {"project", "contract", "case", "manifest"}:
            paths[key] = Path(value)
    return paths


def _graph_runtime_inputs(
    root: Path, spec: Any
) -> tuple[
    str | None,
    str | None,
    dict[str, tuple[str, ...]],
    str | None,
    tuple[str, ...],
    tuple[GraphNode, ...],
    tuple[GraphEdge, ...],
    GraphExport | None,
]:
    values: dict[str, str] = {}
    candidate_refs: dict[str, list[str]] = {}
    for item in spec.inputs:
        key, separator, value = item.partition("=")
        if not separator:
            continue
        if key in {"graph_target", "graph_mode", "graph_dir", "graph_freshness_state"}:
            values[key] = value
        elif key == "graph_candidate_ref":
            candidate, candidate_separator, node_id = value.partition("=")
            if candidate_separator and candidate and node_id:
                candidate_refs.setdefault(candidate, []).append(node_id)
    target = values.get("graph_target")
    refs = {key: tuple(sorted(set(value))) for key, value in sorted(candidate_refs.items())}
    if target is None:
        return None, None, refs, None, (), (), (), None
    evidence: set[str] = set()
    graph_dir_value = values.get("graph_dir")
    if graph_dir_value is None:
        evidence.add("graph:directory-missing")
        return (
            target,
            values.get("graph_mode"),
            refs,
            "unresolved",
            tuple(sorted(evidence)),
            (),
            (),
            None,
        )
    graph_dir = Path(graph_dir_value)
    if not graph_dir.is_absolute():
        graph_dir = root / graph_dir
    try:
        nodes, edges = read_graph(graph_dir)
    except ContractError as exc:
        evidence.add(f"graph:load:{exc.code}")
        return (
            target,
            values.get("graph_mode"),
            refs,
            "unresolved",
            tuple(sorted(evidence)),
            (),
            (),
            None,
        )
    snapshot: GraphExport | None = None
    export_path = graph_dir / "export.json"
    if export_path.is_file():
        try:
            snapshot = GraphExport.model_validate(
                json.loads(export_path.read_text(encoding="utf-8"))
            )
        except (OSError, UnicodeDecodeError, ValueError):
            evidence.add("graph:export:unresolved")
    return (
        target,
        values.get("graph_mode"),
        refs,
        values.get("graph_freshness_state", "fresh"),
        tuple(sorted(evidence)),
        tuple(nodes),
        tuple(edges),
        snapshot,
    )


def _persist_evolution_gate(
    storage: RunStore,
    routing: RoutingDecision,
    run_id: str,
    timestamp: str,
) -> PromotionGate:
    """Persist the evidence gate that authorizes or refuses route execution."""
    policy = load_evolution_policy()
    gate = decide_promotion(
        decision_id=routing.decision_id,
        policy=policy,
        required_evidence=("task_spec", "routing_decision"),
        available_evidence=available_routing_evidence(routing),
        rollback_ref=f"{run_id}:static-routing",
    )
    storage.save_evolution(gate)
    storage.event(
        TrajectoryEvent(
            event_id=stable_id("event", {"run": run_id, "event": "routing_evolution_gate"}),
            run_id=run_id,
            event="routing_evolution_gate",
            actor="api-orchestrator",
            subject=routing.decision_id,
            payload={
                "mode": gate.mode,
                "state": gate.state,
                "coverage": gate.coverage.model_dump(mode="json"),
                "fallback": gate.fallback,
                "gaps": gate.gaps,
                "policy_version": gate.policy_version,
                "rollback_ref": gate.rollback_ref,
            },
            created_at=timestamp,
        )
    )
    return gate


def _blocked_by_evolution_gate(
    run: AgenticRun,
    storage: RunStore,
    routing_id: str,
    gate: PromotionGate,
    timestamp: str,
) -> dict[str, object]:
    """Return a governed result when route promotion is not active."""
    status = "BLOCKED" if gate.state == "blocked" else "REVIEW"
    gap = (
        f"AF-EVOLUTION-PROMOTION: field=mode/state; unlock=resolve the evidence gate "
        f"before active execution ({gate.state})"
    )
    updated = run.model_copy(
        update={
            "state": AgenticState.BLOCKED
            if status == "BLOCKED"
            else AgenticState.AWAITING_SUPERVISION,
            "final_status": status,
            "decision_ids": (routing_id,),
            "gaps": tuple(sorted({*gate.gaps, gap})),
            "finished_at": timestamp,
        }
    )
    storage.save_run(updated)
    return {
        "run": updated.model_dump(mode="json"),
        "artifacts": [],
        "status": status,
        "evolution": gate.model_dump(mode="json"),
        "run_dir": str(storage.directory),
    }


def _effective_policy(policy: Any, task_max_calls: int, economy: EconomyPlan) -> Any:
    envelope = economy.envelope
    return policy.model_copy(
        update={
            "max_calls": max(1, min(policy.max_calls, task_max_calls, envelope.provider_calls)),
            "max_rounds": max(1, min(policy.max_rounds, envelope.debate_rounds or 1)),
        }
    )


def _governed_policy(policy: Any, decision: Any) -> Any:
    """Apply governor ceilings without widening a caller's policy."""
    return policy.model_copy(
        update={
            "max_parallel_agents": min(policy.max_parallel_agents, max(1, decision.max_agents)),
            "max_rounds": min(policy.max_rounds, max(1, decision.max_debates or 1)),
            "max_retries": min(policy.max_retries, decision.max_retries),
        }
    )


def _strategy_payload(routing_plan: Any, policy: Any) -> dict[str, JsonValue]:
    return {
        "primary": routing_plan.primary,
        "fallbacks": routing_plan.fallbacks,
        "execution_mode": routing_plan.execution_mode,
        "parallel": policy.max_parallel_agents,
    }


def _record_strategy(
    storage: RunStore,
    run_id: str,
    strategy: dict[str, JsonValue],
    timestamp: str,
) -> LoopDetection:
    policy = load_loop_policy()
    fingerprint = strategy_fingerprint(strategy)
    history = storage.strategy_history()
    detection = check_loop(
        (*history, fingerprint),
        window=int(policy["window"]),
        max_repeats=int(policy["max_repeats"]),
        blocked_action=cast(LoopAction, str(policy["blocked_action"])),
    )
    storage.event(
        TrajectoryEvent(
            event_id=stable_id(
                "event",
                {"run": run_id, "event": "strategy_selected", "fingerprint": fingerprint},
            ),
            run_id=run_id,
            event="strategy_selected",
            actor="api-orchestrator",
            subject=fingerprint,
            payload={
                "fingerprint": fingerprint,
                "strategy": strategy,
                "history_length": len(history),
                "loop": detection.model_dump(mode="json"),
            },
            created_at=timestamp,
            evidence_level="observed",
        )
    )
    return detection


def _governor_complexity(routing: RoutingDecision) -> str | None:
    assessment = routing.risk_complexity
    if assessment is None:
        return None
    return {
        "simple": "low",
        "moderate": "medium",
        "complex": "high",
        "critical": "high",
    }.get(assessment.complexity)


def _exhausted(missing: int) -> str:
    return (
        f"AF-BUDGET-EXHAUSTED: {missing} planned invocation(s) exceeded the economy call budget; "
        "field=profile; unlock=rerun with --profile balanced|deep or raise TaskSpec budgets"
    )


def _recovery_for_error(error: str) -> RecoveryDecision:
    """First classification point for a post-invocation error (e.g. a payload
    validation gap the scheduler never saw). Invocation failures already carry
    the canonical ``InvocationResult.recovery`` — never reclassified here."""
    return decide_recovery(classify_failure("", error), 0)


def _economy_block(
    economy: EconomyPlan,
    ladder: list[LadderStep],
    gaps: list[str],
    max_calls: int,
    reserve: int,
    reserve_left: int,
    calls_used: int,
) -> dict[str, object]:
    codes = {gap.split(":", 1)[0] for gap in gaps}
    codes |= {item.split(":", 1)[0] for item in economy.diagnostics}
    return {
        "requested": economy.requested,
        "requested_source": economy.requested_source,
        "effective": economy.effective,
        "escalation_reason": economy.escalation_reason,
        "trimmed_roles": list(economy.trimmed_roles),
        "stopped_at": ladder[-1].level if ladder else "L2",
        "ladder": [step.model_dump(mode="json") for step in ladder],
        "max_calls": max_calls,
        "reserve_calls": reserve,
        "reserve_left_at_verification": reserve_left,
        "calls_used": calls_used,
        "debate_rounds": economy.envelope.debate_rounds,
        "status": "unresolved" if gaps else "ok",
        "codes": sorted(codes),
    }


def economy_gaps_codes(block: dict[str, object]) -> tuple[str, ...]:
    """Codes of an unresolved economy block; an ok block carries none into the checkpoint."""
    codes = block.get("codes")
    if block.get("status") != "unresolved" or not isinstance(codes, list):
        return ()
    return tuple(str(code) for code in codes)


def _economy_stop(
    run: AgenticRun,
    storage: RunStore,
    decision_id: str,
    economy: EconomyPlan,
    proof: DeterministicProof,
    policy: Any,
    timestamp: str,
    root: Path,
) -> dict[str, object]:
    ladder = [
        LadderStep(
            level="L0",
            action="deterministic proof",
            trigger=f"run={proof.run_ref}; proofs={','.join(proof.proofs)}",
        )
    ]
    block = _economy_block(economy, ladder, [], policy.max_calls, 0, policy.max_calls, 0)
    stopped = run.model_copy(
        update={
            "state": AgenticState.AWAITING_SUPERVISION,
            "final_status": "REVIEW",
            "decision_ids": (decision_id,),
            "finished_at": timestamp,
        }
    )
    storage.save_run(stopped)
    storage.json("summary.json", {"run_id": run.run_id, "economy": block, "errors": []})
    task_store.record_agentic_run(root, stopped)
    task_store.record_event(
        root,
        run.task_id,
        {"event": "agentic_run", "run_id": run.run_id, "status": "REVIEW", "economy": "L0"},
    )
    return {
        "run": stopped.model_dump(mode="json"),
        "artifacts": [],
        "status": "REVIEW",
        "economy": block,
        "run_dir": str(storage.directory),
    }


class _Escalation:
    def __init__(self) -> None:
        self.steps: list[LadderStep] = []
        self.gaps: list[str] = []
        self.errors: list[str] = []
        self.artifact: AgentArtifact | None = None


async def _escalate(
    economy: EconomyPlan,
    artifacts: list[AgentArtifact],
    config: dict[str, Any],
    remaining: int,
    control: ControlPlane,
    control_run_id: str,
    control_steps: dict[str, Any],
    capabilities_catalog: dict[str, Any],
    adapter: ModelAdapter,
    spec: Any,
    run_id: str,
    storage: RunStore,
    policy: Any,
    role_rows: dict[str, RoleContext] | None = None,
) -> _Escalation:
    outcome = _Escalation()
    reviewer = economy.escalation_reviewer
    threshold = float(config.get("triggers", {}).get("low_confidence", 0.7))
    triggers = needs_escalation(
        [item.confidence for item in artifacts if item.confidence is not None],
        [gap for item in artifacts for gap in item.unresolved],
        [_recommendation(item) for item in artifacts],
        threshold,
    )
    step = control_steps.get(reviewer) if reviewer is not None else None
    if not triggers or reviewer is None or step is None:
        if step is not None:
            control.skip(control_run_id, step.step_id, "AF-ECONOMY-ESCALATION-NOT-USED")
        return outcome
    if not allows(economy, "L3"):
        control.skip(control_run_id, step.step_id, "AF-ECONOMY-CEILING")
        outcome.gaps.append(
            "AF-ECONOMY-CEILING: field=profile; unlock=rerun with --profile balanced|deep "
            f"to allow an escalation review ({','.join(triggers)})"
        )
        return outcome
    if remaining <= 0:
        control.skip(control_run_id, step.step_id, "AF-BUDGET-EXHAUSTED")
        outcome.gaps.append(_exhausted(1))
        return outcome
    control.start(control_run_id, step.step_id)
    invocation = AgentInvocation(
        invocation_id=stable_id("inv", {"run": run_id, "capability": reviewer}),
        run_id=run_id,
        agent=capabilities_catalog[reviewer].agent,
        capability=reviewer,
        adapter=adapter.name,
        dependencies=(),
        input_refs=spec.inputs,
        idempotency_key=step.idempotency_key,
    )

    async def worker(item: AgentInvocation) -> object:
        return await _authorized_invoke(
            adapter,
            AgentRequest(
                invocation_id=item.invocation_id,
                agent=item.agent,
                capability=item.capability,
                prompt=f"Escalation review for capability {item.capability}",
                input_refs=item.input_refs,
                output_contract="AgentArtifact/v1",
                authority_subject=capabilities_catalog[reviewer].kind,
                delegated_from="api-orchestrator",
                **_role_fields(
                    (role_rows or {}).get(item.capability),
                    tuple(f"artifact:{artifact.artifact_id}" for artifact in artifacts),
                ),
            ),
        )

    results = await run_bounded(
        (invocation,),
        worker,
        limit=1,
        timeout_seconds=policy.timeout_seconds,
        max_calls=remaining,
        max_retries=policy.max_retries,
    )
    outcome.steps.append(
        LadderStep(level="L3", action="escalation review", trigger=",".join(triggers), calls=1)
    )
    result = results[0] if results else None
    if result is None or result.error is not None or result.response is None:
        error = (result.error if result else None) or "escalation review failed"
        outcome.errors.append(f"{reviewer}: {error}")
        control.fail(control_run_id, step.step_id, error)
        return outcome
    payload = _json_payload(result.response)
    gaps = validate_agent_payload(payload)
    if gaps:
        outcome.errors.extend(f"{reviewer}: {gap}" for gap in gaps)
        control.fail(control_run_id, step.step_id, "; ".join(gaps))
        return outcome
    artifact = AgentArtifact(
        artifact_id=stable_id("artifact", {"run": run_id, "invocation": invocation.invocation_id}),
        run_id=run_id,
        invocation_id=invocation.invocation_id,
        agent=invocation.agent,
        capability=reviewer,
        kind=ArtifactKind.SPECIALIST,
        schema_name="AgentArtifact/v1",
        payload=payload,
        evidence=_strings(payload, "facts"),
        assumptions=_strings(payload, "assumptions"),
        risks=_strings(payload, "risks"),
        unresolved=_strings(payload, "unresolved"),
        confidence=_confidence(payload),
        content_sha256=content_hash(payload),
    )
    control.complete(control_run_id, step.step_id, artifact.model_dump(mode="json"))
    storage.artifact(artifact)
    outcome.artifact = artifact
    return outcome


def _role_fields(row: RoleContext | None, extra_refs: tuple[str, ...] = ()) -> dict[str, Any]:
    if row is None:
        return {}
    return {
        "context_class": row.context_class,
        "context_refs": (*row.refs, *row.artifact_refs, *extra_refs),
        "expertise": row.expertise,
        "prompt_prefix_sha256": row.prompt_prefix_sha256,
    }


async def _authorized_invoke(adapter: ModelAdapter, request: AgentRequest) -> object:
    """Enforce runtime tool admission before crossing the model adapter boundary."""
    profiles, permissions = load_tool_risk()
    boundary = authorize(
        "api-orchestrator", "agent-invocation", profiles=profiles, permissions=permissions
    )
    decisions: tuple[Any, ...] = (boundary,)
    if boundary.decision == "allow":
        subject = request.authority_subject or request.agent
        decisions += tuple(
            authorize(
                subject,
                tool,
                profiles=profiles,
                permissions=permissions,
                delegated_from=request.delegated_from,
                delegated_scope=request.delegated_scope or request.tool_names,
            )
            for tool in request.tool_names
        )
    for decision in decisions:
        if decision.decision != "allow":
            error = ContractError(decision.code or "AF-TOOL-AUTHZ-DENIED", decision.reason)
            error.field = decision.field or "tool"  # type: ignore[attr-defined]
            error.unlock = decision.unlock or "declare an explicit runtime tool grant"  # type: ignore[attr-defined]
            raise error
    return await adapter.invoke(request)


def _shadow_mode(spec: Any) -> str:
    for item in getattr(spec, "inputs", ()) or ():
        if str(item).strip() == "shadow_mode=capability_eval":
            return "capability_eval"
    return "paired_ab"


async def _shadow(
    economy: EconomyPlan,
    challengers: tuple[str, ...],
    calls_available: int,
    artifacts: list[AgentArtifact],
    primary: str | None,
    capabilities_catalog: dict[str, Any],
    adapter: ModelAdapter,
    spec: Any,
    run_id: str,
    storage: RunStore,
    policy: Any,
    role_rows: dict[str, RoleContext],
    *,
    control: ControlPlane,
    control_run_id: str,
) -> ShadowDecision:
    """Observational challenger run; never touches artifacts, gaps or status.

    The call is accounted by the ControlPlane like any step, so ``calls_used``
    and the economy checkpoint match real adapter invocations. ``paired_ab``
    (default) gives the challenger the primary's context; ``capability_eval``
    (TaskSpec input ``shadow_mode=capability_eval``) builds its own.
    """
    known = tuple(name for name in challengers if name in capabilities_catalog)
    mode = _shadow_mode(spec)
    decision = decide_shadow(
        run_id, economy.envelope.shadow_share, known, calls_available
    ).model_copy(update={"mode": mode})
    if decision.challenger is None or not decision.sampled or calls_available < 1:
        return decision
    name = decision.challenger
    try:
        control.record_call(control_run_id, "shadow")
    except ContractError as exc:
        return decision.model_copy(update={"reason": f"{exc.code}: shadow call not accounted"})
    context_row = role_rows.get(primary or "")
    if mode == "capability_eval":
        from apiforge.runtime.role_context import plan_roles

        own = plan_roles(
            storage.root,
            spec,
            ((name, "specialist"),),
            context_bytes=max(
                256, int(economy.envelope.context_bytes * economy.envelope.shadow_share)
            ),
            run_id=run_id,
        )
        context_row = own.roles[0] if own.roles else None
    invocation = AgentInvocation(
        invocation_id=stable_id("inv", {"run": run_id, "shadow": name}),
        run_id=run_id,
        agent=capabilities_catalog[name].agent,
        capability=name,
        adapter=adapter.name,
        input_refs=spec.inputs,
    )

    async def worker(item: AgentInvocation) -> object:
        return await _authorized_invoke(
            adapter,
            AgentRequest(
                invocation_id=item.invocation_id,
                agent=item.agent,
                capability=item.capability,
                prompt=f"Shadow challenger for capability {item.capability}",
                input_refs=item.input_refs,
                output_contract="AgentArtifact/v1",
                authority_subject=capabilities_catalog[name].kind,
                delegated_from="api-orchestrator",
                **_role_fields(context_row),
            ),
        )

    results = await run_bounded(
        (invocation,),
        worker,
        limit=1,
        timeout_seconds=policy.timeout_seconds,
        max_calls=1,
        max_retries=0,
    )
    result = results[0] if results else None
    if result is None or result.error is not None or result.response is None:
        return decision.model_copy(
            update={"calls": len(results), "reason": "shadow challenger failed; ignored"}
        )
    payload = _json_payload(result.response)
    champion = next((item for item in artifacts if item.capability == primary), None)
    agreement = (
        str(payload.get("recommendation", "")) == _recommendation(champion)
        if champion is not None
        else None
    )
    storage.json(
        f"shadow-{name}.json",
        {"capability": name, "payload": payload, "agreement": agreement, "primary": primary},
    )
    return decision.model_copy(update={"executed": True, "calls": 1, "agreement": agreement})


async def execute_run(
    root: Path,
    task_id: str,
    *,
    adapter: ModelAdapter,
    policy_id: str = "local-ci-safe",
    now: str | None = None,
    requested_debate: bool = False,
    profile: str | None = None,
    economy_enabled: bool = True,
) -> dict[str, object]:
    root = Path(root)
    spec = task_store.load(root, task_id)
    economy_config = load_economy_config() if economy_enabled else None
    if economy_enabled:
        validate_profile(profile)
    timestamp = _now(now)
    policy = load_policy(policy_id)
    run_id = _run_id(task_id, spec.revision, timestamp)
    storage = RunStore(root, task_id, run_id)
    run = AgenticRun(
        run_id=run_id,
        task_id=task_id,
        revision=spec.revision,
        state=AgenticState.CREATED,
        policy_id=policy.policy_id,
        started_at=timestamp,
    )
    storage.save_run(run)
    storage.event(
        TrajectoryEvent(
            event_id=stable_id("event", {"run": run_id, "event": "created"}),
            run_id=run_id,
            event="created",
            actor="api-orchestrator",
            created_at=timestamp,
        )
    )
    review = build_runtime_review(root, spec)
    findings = review_task_spec(root, spec)
    storage.json("review.json", review.model_dump(mode="json"))
    if findings:
        gaps = tuple(str(item["message"]) for item in findings)
        blocked = any(item.get("severity") == "high" for item in findings)
        final = "BLOCKED" if blocked else "REVIEW"
        run = run.model_copy(
            update={
                "state": AgenticState.BLOCKED if blocked else AgenticState.AWAITING_SUPERVISION,
                "final_status": final,
                "gaps": gaps,
                "finished_at": timestamp,
            }
        )
        storage.save_run(run)
        storage.json("review-findings.json", {"findings": findings})
        task_store.record_event(
            root, task_id, {"event": "agentic_review", "run_id": run_id, "findings": findings}
        )
        return {
            "run": run.model_dump(mode="json"),
            "findings": findings,
            "status": final,
            "run_dir": str(storage.directory),
        }

    capabilities_catalog = load_capabilities()
    scorecards = load_scorecards(root)
    routing_policy = load_routing_policy()
    (
        graph_target,
        graph_mode,
        graph_candidate_refs,
        graph_freshness_state,
        graph_evidence,
        graph_nodes,
        graph_edges,
        graph_snapshot,
    ) = _graph_runtime_inputs(root, spec)
    routing_request = build_routing_request(
        spec,
        policy_id=routing_policy.policy_id,
        available_evidence=("task_spec",),
        graph_target=graph_target,
        graph_mode=graph_mode,
        graph_candidate_refs=graph_candidate_refs,
        graph_freshness_state=graph_freshness_state,
        graph_evidence=graph_evidence,
    )
    routing = route_capabilities(
        capabilities_catalog,
        load_profiles(),
        routing_request,
        policy=routing_policy,
        scorecards=scorecards,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        graph_snapshot=graph_snapshot,
    )
    storage.save_routing(routing)
    if routing.graph_impact is not None:
        storage.save_graph_impact(routing.graph_impact)
    if routing.shadow_evaluation is not None:
        storage.save_shadow_evaluation(routing.shadow_evaluation)
    routing_plan = build_routing_plan(routing, capabilities_catalog, policy=routing_policy)
    planned_challengers = routing_plan.challenger_order
    economy_plan: EconomyPlan | None = None
    if economy_config is not None:
        economy_plan = build_economy_plan(
            routing, spec, flag=profile, manifest=manifest_profile(root), config=economy_config
        )
        routing_plan, economy_plan = apply_economy(
            routing_plan,
            economy_plan,
            routing,
            {name: item.kind for name, item in capabilities_catalog.items()},
        )
        routing = routing.model_copy(update={"economy": economy_plan})
        storage.save_routing(routing)
        storage.json("economy.json", economy_plan.model_dump(mode="json"))
        policy = _effective_policy(policy, spec.budgets.max_calls, economy_plan)
    governor_profile = (
        economy_plan.effective
        if economy_plan is not None
        else (profile if profile in {"economy", "balanced", "deep"} else "balanced")
    )
    governor_inputs = GovernorInputs(
        profile=cast(Any, governor_profile),
        risk=cast(Any, spec.risk.value),
        budget_remaining={"calls": policy.max_calls},
        task_complexity=cast(Any, _governor_complexity(routing)),
    )
    governor_decision = govern(governor_inputs)
    governance_context = RunGovernanceContext(
        context_id=stable_id(
            "governance",
            {"run": run_id, "risk": spec.risk.value, "profile": governor_decision.profile},
        ),
        run_id=run_id,
        task_id=task_id,
        inputs=governor_inputs,
        decision=governor_decision,
        evidence_refs=tuple(sorted(set(routing.evidence))),
        unresolved=governor_decision.unresolved,
    )
    policy = _governed_policy(policy, governor_decision)
    strategy = _strategy_payload(routing_plan, policy)
    loop_detection = _record_strategy(storage, run_id, strategy, timestamp)
    governance_unresolved = set(governance_context.unresolved)
    if loop_detection.code:
        governance_unresolved.add(loop_detection.code)
    governance_context = governance_context.model_copy(
        update={
            "loop": loop_detection,
            "unresolved": tuple(sorted(governance_unresolved)),
        }
    )
    storage.json("governance-context.json", governance_context.model_dump(mode="json"))
    storage.event(
        TrajectoryEvent(
            event_id=stable_id("event", {"run": run_id, "event": "governance_context"}),
            run_id=run_id,
            event="governance_context",
            actor="api-orchestrator",
            subject=governance_context.context_id,
            payload=governance_context.model_dump(mode="json"),
            created_at=timestamp,
        )
    )
    run = run.model_copy(update={"governance_context_id": governance_context.context_id})
    storage.save_run(run)
    storage.save_routing_plan(routing_plan)
    storage.event(
        TrajectoryEvent(
            event_id=stable_id(
                "event", {"run": run_id, "event": "routing", "decision": routing.decision_id}
            ),
            run_id=run_id,
            event="routing_decision",
            actor="api-orchestrator",
            subject=routing.decision_id,
            payload={
                "assessment": (
                    routing.risk_complexity.model_dump(mode="json")
                    if routing.risk_complexity is not None
                    else None
                ),
                "selected": routing.selected,
                "fallback_order": routing.fallback_order,
                "routing_plan": routing_plan.model_dump(mode="json"),
                "shadow_evaluation": (
                    routing.shadow_evaluation.model_dump(mode="json")
                    if routing.shadow_evaluation is not None
                    else None
                ),
                "evidence": routing.evidence,
                "unresolved": routing.unresolved,
            },
            created_at=timestamp,
        )
    )
    if loop_detection.blocked:
        gap = (
            "AF-GOV-LOOP-DETECTED: field=strategy_fingerprint; "
            "unlock=change strategy or provide an approved recovery action"
        )
        run = run.model_copy(
            update={
                "state": AgenticState.BLOCKED,
                "final_status": "BLOCKED",
                "decision_ids": (routing.decision_id,),
                "gaps": tuple(sorted({*run.gaps, gap})),
                "finished_at": timestamp,
            }
        )
        storage.save_run(run)
        storage.event(
            TrajectoryEvent(
                event_id=stable_id("event", {"run": run_id, "event": "governance_loop_blocked"}),
                run_id=run_id,
                event="governance_loop_blocked",
                actor="api-orchestrator",
                subject=loop_detection.strategy_fingerprint,
                payload={"loop": loop_detection.model_dump(mode="json")},
                created_at=timestamp,
            )
        )
        storage.json("replay.json", storage.replay())
        task_store.record_agentic_run(root, run)
        task_store.record_event(
            root,
            task_id,
            {
                "event": "agentic_run",
                "run_id": run_id,
                "status": "BLOCKED",
                "reason": "AF-GOV-LOOP-DETECTED",
            },
        )
        return {
            "run": run.model_dump(mode="json"),
            "artifacts": [],
            "governance": governance_context.model_dump(mode="json"),
            "status": "BLOCKED",
            "unresolved": {"governance": list(governance_context.unresolved)},
            "run_dir": str(storage.directory),
        }
    evolution_gate = _persist_evolution_gate(storage, routing, run_id, timestamp)
    if not is_active(evolution_gate):
        return _blocked_by_evolution_gate(
            run,
            storage,
            routing.decision_id,
            evolution_gate,
            timestamp,
        )
    ladder: list[LadderStep] = []
    economy_gaps: list[str] = []
    if economy_plan is not None:
        proof = deterministic_proof(root, spec)
        if proof.level == "L0":
            return _economy_stop(
                run, storage, routing.decision_id, economy_plan, proof, policy, timestamp, root
            )
        if proof.level == "L1":
            ladder.append(
                LadderStep(
                    level="L1",
                    action="deterministic evidence partial",
                    trigger="missing="
                    + ",".join(proof.missing)
                    + "".join(f"; {note.split(':', 1)[0]}" for note in proof.diagnostics),
                )
            )
    initial_names = tuple(
        name
        for name in (
            routing_plan.primary,
            *routing_plan.parallel,
            *routing_plan.reviewers,
            routing_plan.critic,
            routing_plan.referee,
        )
        if name is not None
    )
    if economy_plan is not None and len(initial_names) > policy.max_calls:
        priority = tuple(
            name
            for name in (
                routing_plan.primary,
                *routing_plan.reviewers,
                routing_plan.critic,
                routing_plan.referee,
                *routing_plan.parallel,
            )
            if name is not None
        )
        initial_names = priority[: policy.max_calls]
        economy_gaps.append(_exhausted(len(priority) - len(initial_names)))
    escalation_names = (
        (economy_plan.escalation_reviewer,)
        if economy_plan is not None and economy_plan.escalation_reviewer is not None
        else ()
    )
    planned_names = tuple(
        dict.fromkeys((*initial_names, *routing_plan.fallbacks, *escalation_names))
    )
    capabilities = tuple(capabilities_catalog[name] for name in planned_names)
    initial_capabilities = tuple(capabilities_catalog[name] for name in initial_names)
    if not planned_names or not initial_capabilities:
        run = run.model_copy(
            update={
                "state": AgenticState.BLOCKED,
                "final_status": "BLOCKED",
                "decision_ids": (routing.decision_id,),
                "gaps": routing.unresolved
                or (
                    (
                        "AF-CAPABILITY-ELIGIBILITY: field=capability; "
                        "unlock=provide the missing evidence or choose a supported capability"
                    ),
                ),
                "finished_at": timestamp,
            }
        )
        storage.save_run(run)
        return {
            "run": run.model_dump(mode="json"),
            "artifacts": [],
            "status": "BLOCKED",
            "run_dir": str(storage.directory),
        }
    control = ControlPlane(root)
    control_run = control.create(
        task_id,
        tuple((item.name, ()) for item in capabilities),
        max_parallel=policy.max_parallel_agents,
        max_calls=policy.max_calls,
        max_retries=policy.max_retries,
        run_id=run_id,
    )
    control_steps = {step.name: step for step in control_run.steps}
    role_rows: dict[str, RoleContext] = {}
    role_plan: RoleContextPlan | None = None
    if economy_plan is not None:
        role_plan = plan_roles(
            root,
            spec,
            tuple((item.name, item.kind) for item in capabilities),
            context_bytes=economy_plan.envelope.context_bytes,
            run_id=run_id,
        )
        role_rows = {row.capability: row for row in role_plan.roles}
        storage.json("role-context.json", role_plan.model_dump(mode="json"))
        economy_gaps.extend(record_roles(root, role_plan))
    invocation_ids = tuple(
        stable_id("inv", {"run": run_id, "capability": item.name}) for item in initial_capabilities
    )
    invocations = tuple(
        AgentInvocation(
            invocation_id=invocation_id,
            run_id=run_id,
            agent=item.agent,
            capability=item.name,
            adapter=adapter.name,
            dependencies=(),
            input_refs=spec.inputs,
            idempotency_key=control_steps[item.name].idempotency_key,
        )
        for invocation_id, item in zip(invocation_ids, initial_capabilities, strict=True)
    )
    all_invocation_ids = list(invocation_ids)
    run = run.model_copy(
        update={
            "state": AgenticState.RUNNING,
            "invocation_ids": invocation_ids,
            "control_run_id": control_run.run_id,
            "decision_ids": (routing.decision_id,),
        }
    )
    storage.save_run(run)
    for step in control_run.steps:
        if step.name not in initial_names:
            continue
        control.start(control_run.run_id, step.step_id)

    async def worker(invocation: AgentInvocation) -> object:
        request = AgentRequest(
            invocation_id=invocation.invocation_id,
            agent=invocation.agent,
            capability=invocation.capability,
            prompt=f"Review API evolution for capability {invocation.capability}",
            input_refs=invocation.input_refs,
            output_contract="AgentArtifact/v1",
            authority_subject=capabilities_catalog[invocation.capability].kind,
            delegated_from="api-orchestrator",
            **_role_fields(role_rows.get(invocation.capability)),
        )
        return await _authorized_invoke(adapter, request)

    reserve = (
        reserve_calls(economy_plan.envelope, policy.max_calls) if economy_plan is not None else 0
    )
    investigation_calls = (
        policy.max_calls - reserve
        if policy.max_calls - reserve >= len(invocations)
        else policy.max_calls
    )
    results = await run_bounded(
        invocations,
        worker,
        limit=policy.max_parallel_agents,
        timeout_seconds=policy.timeout_seconds,
        max_calls=investigation_calls,
        max_retries=policy.max_retries,
        parallelism=lambda ready, remaining: min(
            policy.max_parallel_agents,
            max(1, ready // 2)
            if spec.risk.value in {"sensitive", "external_mutation", "destructive", "irreversible"}
            else ready,
        ),
    )
    if economy_plan is not None:
        ladder.append(
            LadderStep(
                level="L2",
                action="primary and risk-required roles",
                trigger="start",
                calls=len(results),
            )
        )
        if len(results) < len(invocations):
            economy_gaps.append(_exhausted(len(invocations) - len(results)))
    artifacts: list[AgentArtifact] = []
    errors: list[str] = []
    # Canonical recovery decisions: the scheduler's InvocationResult.recovery
    # governs invocation failures; the supervisor only classifies errors that
    # never passed through the scheduler (post-invocation validation gaps).
    recovery_decisions: list[RecoveryDecision] = []
    for result in results:
        control_step = control_steps[result.invocation.capability]
        if result.error is not None or result.response is None:
            errors.append(result.error or "invocation failed")
            if result.recovery is not None:
                recovery_decisions.append(result.recovery)
            elif result.invocation.error_code != "AF-RUNTIME-DEPENDENCY-FAILED":
                recovery_decisions.append(_recovery_for_error(result.error or "invocation failed"))
            control.fail(
                control_run.run_id, control_step.step_id, result.error or "invocation failed"
            )
            continue
        try:
            payload = _json_payload(result.response)
        except (ContractError, ValueError) as exc:
            # A non-contract adapter payload is a governed failure, not a run
            # crash: first classification point produces the decision.
            error = str(exc)
            errors.append(f"{result.invocation.capability}: {error}")
            recovery_decisions.append(_recovery_for_error(error))
            control.fail(control_run.run_id, control_step.step_id, error)
            continue
        guardrail_gaps = validate_agent_payload(payload)
        if guardrail_gaps:
            errors.extend(f"{result.invocation.capability}: {gap}" for gap in guardrail_gaps)
            recovery_decisions.append(_recovery_for_error("; ".join(guardrail_gaps)))
            control.fail(control_run.run_id, control_step.step_id, "; ".join(guardrail_gaps))
            continue
        artifact_id = stable_id(
            "artifact", {"run": run_id, "invocation": result.invocation.invocation_id}
        )
        artifact = AgentArtifact(
            artifact_id=artifact_id,
            run_id=run_id,
            invocation_id=result.invocation.invocation_id,
            agent=result.invocation.agent,
            capability=result.invocation.capability,
            kind=ArtifactKind.SPECIALIST,
            schema_name="AgentArtifact/v1",
            payload=payload,
            evidence=_strings(payload, "facts"),
            assumptions=_strings(payload, "assumptions"),
            risks=_strings(payload, "risks"),
            unresolved=_strings(payload, "unresolved"),
            confidence=_confidence(payload),
            content_sha256=content_hash(payload),
        )
        artifacts.append(artifact)
        control.complete(control_run.run_id, control_step.step_id, artifact.model_dump(mode="json"))
        storage.artifact(artifact)
        storage.event(
            TrajectoryEvent(
                event_id=stable_id(
                    "event",
                    {
                        "run": run_id,
                        "invocation": result.invocation.invocation_id,
                        "event": "checkpoint",
                    },
                ),
                run_id=run_id,
                event="invocation_checkpoint",
                actor="api-orchestrator",
                subject=result.invocation.invocation_id,
                payload={
                    "artifact_id": artifact.artifact_id,
                    "content_sha256": artifact.content_sha256,
                },
                created_at=timestamp,
            )
        )

    primary_succeeded = any(
        result.invocation.capability == routing_plan.primary
        and result.error is None
        and result.response is not None
        for result in results
    )
    if primary_succeeded:
        for fallback in routing_plan.fallbacks:
            fallback_step = control_steps[fallback]
            control.skip(
                control_run.run_id,
                fallback_step.step_id,
                "AF-ROUTING-FALLBACK-NOT-USED: primary completed successfully",
            )
    elif routing_plan.execution_mode == "sequential_failover":
        for fallback in routing_plan.fallbacks:
            fallback_step = control_steps[fallback]
            control.start(control_run.run_id, fallback_step.step_id)
            fallback_invocation = AgentInvocation(
                invocation_id=stable_id("inv", {"run": run_id, "capability": fallback}),
                run_id=run_id,
                agent=capabilities_catalog[fallback].agent,
                capability=fallback,
                adapter=adapter.name,
                dependencies=(),
                input_refs=spec.inputs,
                idempotency_key=fallback_step.idempotency_key,
                retry_count=fallback_step.attempts,
            )
            all_invocation_ids.append(fallback_invocation.invocation_id)
            fallback_results = await run_bounded(
                (fallback_invocation,),
                worker,
                limit=1,
                timeout_seconds=policy.timeout_seconds,
                max_calls=max(
                    0, policy.max_calls - reserve - control.get(control_run.run_id).calls_used
                ),
                max_retries=policy.max_retries,
            )
            if not fallback_results:
                error = f"{fallback}: AF-CONTROL-BUDGET: no fallback call remained"
                errors.append(error)
                recovery_decisions.append(_recovery_for_error(error))
                control.skip(
                    control_run.run_id,
                    fallback_step.step_id,
                    "AF-ROUTING-FALLBACK-BUDGET: no call budget remained",
                )
                continue
            fallback_result = fallback_results[0]
            if fallback_result.error is not None or fallback_result.response is None:
                error = fallback_result.error or "fallback invocation failed"
                errors.append(f"{fallback}: {error}")
                if fallback_result.recovery is not None:
                    recovery_decisions.append(fallback_result.recovery)
                else:
                    recovery_decisions.append(_recovery_for_error(error))
                failed_run = control.fail(control_run.run_id, fallback_step.step_id, error)
                if (
                    next(item for item in failed_run.steps if item.name == fallback).status
                    == "pending"
                ):
                    control.skip(
                        control_run.run_id,
                        fallback_step.step_id,
                        f"AF-ROUTING-FALLBACK-FAILED: {error}",
                    )
                continue
            try:
                payload = _json_payload(fallback_result.response)
            except (ContractError, ValueError) as exc:
                error = f"{fallback}: {exc}"
                errors.append(error)
                recovery_decisions.append(_recovery_for_error(error))
                control.fail(control_run.run_id, fallback_step.step_id, error)
                continue
            fallback_gaps = validate_agent_payload(payload)
            if fallback_gaps:
                error = "; ".join(fallback_gaps)
                errors.extend(f"{fallback}: {error}" for _ in [0])
                recovery_decisions.append(_recovery_for_error(error))
                failed_run = control.fail(control_run.run_id, fallback_step.step_id, error)
                if (
                    next(item for item in failed_run.steps if item.name == fallback).status
                    == "pending"
                ):
                    control.skip(
                        control_run.run_id,
                        fallback_step.step_id,
                        f"AF-ROUTING-FALLBACK-INVALID: {error}",
                    )
                continue
            artifact = AgentArtifact(
                artifact_id=stable_id(
                    "artifact",
                    {"run": run_id, "invocation": fallback_result.invocation.invocation_id},
                ),
                run_id=run_id,
                invocation_id=fallback_result.invocation.invocation_id,
                agent=fallback_result.invocation.agent,
                capability=fallback_result.invocation.capability,
                kind=ArtifactKind.SPECIALIST,
                schema_name="AgentArtifact/v1",
                payload=payload,
                evidence=_strings(payload, "facts"),
                assumptions=_strings(payload, "assumptions"),
                risks=_strings(payload, "risks"),
                unresolved=_strings(payload, "unresolved"),
                confidence=_confidence(payload),
                content_sha256=content_hash(payload),
            )
            artifacts.append(artifact)
            control.complete(
                control_run.run_id, fallback_step.step_id, artifact.model_dump(mode="json")
            )
            storage.artifact(artifact)
            storage.event(
                TrajectoryEvent(
                    event_id=stable_id(
                        "event",
                        {"run": run_id, "invocation": artifact.invocation_id, "event": "fallback"},
                    ),
                    run_id=run_id,
                    event="fallback_checkpoint",
                    actor="api-orchestrator",
                    subject=artifact.invocation_id,
                    payload={"artifact_id": artifact.artifact_id},
                    created_at=timestamp,
                )
            )
            for unused in routing_plan.fallbacks[routing_plan.fallbacks.index(fallback) + 1 :]:
                unused_step = control_steps[unused]
                control.skip(
                    control_run.run_id,
                    unused_step.step_id,
                    "AF-ROUTING-FALLBACK-NOT-USED: earlier fallback completed successfully",
                )
            break

    # The scheduler's InvocationResult.recovery is the canonical decision for
    # every invocation failure; recovery_decisions was collected in error
    # order during processing, so the first entry governs the run's outcome.
    recovery = recovery_decisions[0] if recovery_decisions else None
    governance_unresolved = set(governance_context.unresolved)
    for decision in recovery_decisions:
        governance_unresolved.update(decision.unresolved)
        if decision.code:
            governance_unresolved.add(decision.code)
    governance_context = governance_context.model_copy(
        update={
            "recovery": recovery,
            "recoveries": tuple(recovery_decisions),
            "loop": loop_detection,
            "unresolved": tuple(sorted(governance_unresolved)),
        }
    )
    storage.json("governance-context.json", governance_context.model_dump(mode="json"))
    storage.event(
        TrajectoryEvent(
            event_id=stable_id("event", {"run": run_id, "event": "governance_postflight"}),
            run_id=run_id,
            event="governance_postflight",
            actor="api-orchestrator",
            subject=governance_context.context_id,
            payload={
                "recovery": recovery.model_dump(mode="json") if recovery else None,
                "loop": loop_detection.model_dump(mode="json"),
            },
            created_at=timestamp,
        )
    )
    reserve_left = policy.max_calls - control.get(control_run.run_id).calls_used
    gain = assess_gain(
        artifacts, float((economy_config or {}).get("triggers", {}).get("low_confidence", 0.7))
    )
    all_unresolved = tuple(item for artifact in artifacts for item in artifact.unresolved)
    confidences = [item.confidence for item in artifacts if item.confidence is not None]
    confidence = min(confidences) if confidences else None
    recommendations = {_recommendation(item) for item in artifacts}
    review_gain = expected_gain(
        "call_reviewer",
        {
            "agreement": 1.0 if len(recommendations) <= 1 and artifacts else None,
            "unresolved_share": (
                min(len(all_unresolved) / max(len(artifacts), 1), 1.0) if artifacts else None
            ),
            "confidence": confidence,
            "remaining_budget": min(reserve_left / max(policy.max_calls, 1), 1.0),
            "role_coverage": min(len(artifacts) / max(len(initial_capabilities), 1), 1.0),
        },
    )
    review_stop = decide_stop(
        review_gain,
        mandatory_requirement=(
            spec.risk.value in policy.critic_risks
            or (
                confidence is not None
                and confidence
                < float((economy_config or {}).get("triggers", {}).get("low_confidence", 0.7))
            )
        ),
    )
    governance_context = governance_context.model_copy(
        update={
            "gain": review_gain,
            "stop": review_stop,
            "unresolved": tuple(
                sorted(
                    set(
                        governance_context.unresolved
                        + review_gain.unresolved
                        + ((review_stop.code,) if review_stop.code else ())
                    )
                )
            ),
        }
    )
    storage.json("governance-context.json", governance_context.model_dump(mode="json"))
    if economy_plan is not None and review_stop.decision == "continue":
        escalated = await _escalate(
            economy_plan,
            artifacts,
            economy_config or {},
            reserve_left,
            control,
            control_run.run_id,
            control_steps,
            capabilities_catalog,
            adapter,
            spec,
            run_id,
            storage,
            policy,
            role_rows,
        )
        ladder.extend(escalated.steps)
        economy_gaps.extend(escalated.gaps)
        errors.extend(escalated.errors)
        if escalated.artifact is not None:
            artifacts.append(escalated.artifact)
            all_invocation_ids.append(escalated.artifact.invocation_id)
    all_unresolved = tuple(item for artifact in artifacts for item in artifact.unresolved)
    confidences = [item.confidence for item in artifacts if item.confidence is not None]
    confidence = min(confidences) if confidences else None
    room, reasons = should_open_room(
        policy=policy,
        risk=spec.risk.value,
        confidence=confidence,
        unresolved=all_unresolved,
        conflicting_facts=len({_recommendation(item) for item in artifacts}) > 1,
        requested_by_user=requested_debate,
    )
    if economy_plan is not None and room and governor_decision.max_debates <= 0:
        room = False
        if not allows(economy_plan, "L4"):
            economy_gaps.append(
                "AF-ECONOMY-CEILING: field=profile; unlock=rerun with --profile balanced|deep "
                f"to allow a debate room ({','.join(reasons)})"
            )
        else:
            economy_gaps.append(
                "AF-GOV-DEBATE-CEILING: field=max_debates; "
                "unlock=use a governor profile that explicitly permits debate"
            )
    if economy_plan is not None and room:
        forced = spec.risk.value in policy.critic_risks or economy_plan.effective == "deep"
        if forced or (allows(economy_plan, "L4") and economy_plan.envelope.debate_rounds > 0):
            ladder.append(LadderStep(level="L4", action="debate room", trigger=",".join(reasons)))
        else:
            room = False
            economy_gaps.append(
                "AF-ECONOMY-CEILING: field=profile; unlock=rerun with --profile balanced|deep "
                f"to allow a debate room ({','.join(reasons)})"
            )
    critic = critic_findings(item.model_dump(mode="json") for item in artifacts)
    critic_required = requires_critic(policy, spec.risk.value)
    gate_reasons = tuple(sorted(set(reasons + (("critic_findings",) if critic else ()))))
    needs_gate = requires_human_gate(policy, gate_reasons) or (critic_required and bool(critic))
    final_status = (
        "REVIEW" if errors or room or needs_gate else "BLOCKED" if not artifacts else "REVIEW"
    )
    run = run.model_copy(
        update={
            "state": AgenticState.AWAITING_SUPERVISION
            if final_status == "REVIEW"
            else AgenticState.BLOCKED,
            "artifact_ids": tuple(item.artifact_id for item in artifacts),
            "invocation_ids": tuple(all_invocation_ids),
            "gaps": tuple(sorted(set(errors + list(critic) + list(all_unresolved) + economy_gaps))),
            "final_status": final_status,
            "finished_at": timestamp,
            "run_digest": content_hash(
                {"run": run_id, "artifacts": [item.model_dump(mode="json") for item in artifacts]}
            ),
        }
    )
    if economy_plan is not None and needs_gate:
        ladder.append(LadderStep(level="L5", action="human gate", trigger=",".join(gate_reasons)))
    shadow_decision: ShadowDecision | None = None
    if economy_plan is not None:
        shadow_decision = await _shadow(
            economy_plan,
            planned_challengers,
            policy.max_calls - control.get(control_run.run_id).calls_used - reserve,
            artifacts,
            routing_plan.primary,
            capabilities_catalog,
            adapter,
            spec,
            run_id,
            storage,
            policy,
            role_rows,
            control=control,
            control_run_id=control_run.run_id,
        )
    economy_block = (
        _economy_block(
            economy_plan,
            ladder,
            economy_gaps,
            policy.max_calls,
            reserve,
            reserve_left,
            control.get(control_run.run_id).calls_used,
        )
        if economy_plan is not None
        else None
    )
    if economy_block is not None:
        economy_block["information_gain"] = gain.model_dump(mode="json")
    storage.save_run(run)
    storage.json(
        "summary.json",
        {
            "run_id": run_id,
            "economy": economy_block,
            "governance": governance_context.model_dump(mode="json"),
            "role_context": role_summary(role_plan) if role_plan is not None else None,
            "shadow": (
                shadow_decision.model_dump(mode="json") if shadow_decision is not None else None
            ),
            "critic_required": critic_required,
            "critic_findings": critic,
            "debate_reasons": reasons,
            "human_gate": needs_gate,
            "errors": errors,
            "unresolved": {
                "routing": list(routing.unresolved),
                "governance": list(governance_context.unresolved),
            },
        },
    )
    if economy_plan is not None and economy_block is not None:
        save_checkpoint(
            storage.directory,
            build_checkpoint(
                run_id=run_id,
                task_id=task_id,
                plan=economy_plan,
                max_calls=policy.max_calls,
                calls_used=control.get(control_run.run_id).calls_used,
                stopped_at=str(economy_block["stopped_at"]),
                now=timestamp,
                codes=tuple(str(code) for code in economy_gaps_codes(economy_block)),
            ),
        )
    storage.json("replay.json", storage.replay())
    task_store.record_agentic_run(root, run)
    task_store.record_event(
        root,
        task_id,
        {
            "event": "agentic_run",
            "run_id": run_id,
            "status": final_status,
            "artifacts": len(artifacts),
            "critic_required": critic_required,
            "debate_reasons": reasons,
        },
    )
    return {
        "run": run.model_dump(mode="json"),
        "artifacts": [item.model_dump(mode="json") for item in artifacts],
        "critic": {"required": critic_required, "findings": critic},
        "debate": {
            "opened": room,
            "reasons": reasons,
            "max_rounds": (
                economy_plan.envelope.debate_rounds
                if economy_plan is not None
                else policy.max_rounds
            ),
        },
        "economy": economy_block,
        "governance": governance_context.model_dump(mode="json"),
        "role_context": role_summary(role_plan) if role_plan is not None else None,
        "shadow": shadow_decision.model_dump(mode="json") if shadow_decision is not None else None,
        "unresolved": {
            "routing": list(routing.unresolved),
            "governance": list(governance_context.unresolved),
        },
        "status": final_status,
        "run_dir": str(storage.directory),
    }


async def resume_existing_run(
    root: Path,
    task_id: str,
    run_id: str,
    *,
    adapter: ModelAdapter,
    policy_id: str = "local-ci-safe",
    now: str | None = None,
    profile: str | None = None,
) -> dict[str, object]:
    root = Path(root)
    spec = task_store.load(root, task_id)
    validate_profile(profile)
    timestamp = _now(now)
    policy = load_policy(policy_id)
    storage = RunStore(root, task_id, run_id)
    previous = storage.load_run()
    if previous is None:
        raise ContractError("AF-RUNTIME-NOT-FOUND", f"no runtime run {run_id!r}")
    checkpoint = load_checkpoint(storage.directory)
    profile, pin_notes = pin_profile(checkpoint, profile)
    control = ControlPlane(root)
    control_run = control.get(run_id)
    if control_run.task_id != task_id:
        raise ContractError("AF-RUNTIME-COMPATIBILITY", "control run task does not match task_id")
    if control_run.status in {"completed", "cancelled", "blocked", "awaiting_review"}:
        return {
            "run": previous.model_dump(mode="json"),
            "status": previous.final_status or "REVIEW",
            "resumed": True,
            "reused_invocations": len(previous.invocation_ids),
            "run_dir": str(storage.directory),
        }
    control.recover_expired(run_id, now=timestamp)
    ready = control.ready(run_id)
    if not ready:
        return {
            "run": previous.model_dump(mode="json"),
            "status": "REVIEW",
            "resumed": True,
            "reused_invocations": len(previous.invocation_ids),
            "gaps": ("AF-CONTROL-NOT-READY: no resumable step",),
            "run_dir": str(storage.directory),
        }
    capabilities = load_capabilities()
    profiles = load_profiles()
    scorecards = load_scorecards(root)
    routing_policy = load_routing_policy()
    (
        graph_target,
        graph_mode,
        graph_candidate_refs,
        graph_freshness_state,
        graph_evidence,
        graph_nodes,
        graph_edges,
        graph_snapshot,
    ) = _graph_runtime_inputs(root, spec)
    routing_request = build_routing_request(
        spec,
        policy_id=routing_policy.policy_id,
        available_evidence=("task_spec",),
        graph_target=graph_target,
        graph_mode=graph_mode,
        graph_candidate_refs=graph_candidate_refs,
        graph_freshness_state=graph_freshness_state,
        graph_evidence=graph_evidence,
    )
    routing = route_capabilities(
        capabilities,
        profiles,
        routing_request,
        policy=routing_policy,
        scorecards=scorecards,
        graph_nodes=graph_nodes,
        graph_edges=graph_edges,
        graph_snapshot=graph_snapshot,
    )
    storage.save_routing(routing)
    if routing.graph_impact is not None:
        storage.save_graph_impact(routing.graph_impact)
    if routing.shadow_evaluation is not None:
        storage.save_shadow_evaluation(routing.shadow_evaluation)
    evolution_gate = _persist_evolution_gate(storage, routing, run_id, timestamp)
    if not is_active(evolution_gate):
        return _blocked_by_evolution_gate(
            previous,
            storage,
            routing.decision_id,
            evolution_gate,
            timestamp,
        )
    by_name = {item.name: item for item in capabilities.values()}
    routing_plan = build_routing_plan(routing, capabilities, policy=routing_policy)
    economy_plan = build_economy_plan(
        routing, spec, flag=profile, manifest=manifest_profile(root), config=load_economy_config()
    )
    routing = routing.model_copy(update={"economy": economy_plan})
    storage.save_routing(routing)
    policy = _effective_policy(policy, spec.budgets.max_calls, economy_plan)
    storage.save_routing_plan(routing_plan)
    strategy = _strategy_payload(routing_plan, policy)
    loop_detection = _record_strategy(storage, run_id, strategy, timestamp)
    if loop_detection.blocked:
        gap = (
            "AF-GOV-LOOP-DETECTED: field=strategy_fingerprint; "
            "unlock=change strategy or provide an approved recovery action"
        )
        resumed = previous.model_copy(
            update={
                "state": AgenticState.BLOCKED,
                "final_status": "BLOCKED",
                "gaps": tuple(sorted({*previous.gaps, gap})),
                "finished_at": timestamp,
            }
        )
        storage.save_run(resumed)
        storage.event(
            TrajectoryEvent(
                event_id=stable_id("event", {"run": run_id, "event": "governance_loop_blocked"}),
                run_id=run_id,
                event="governance_loop_blocked",
                actor="api-orchestrator",
                subject=loop_detection.strategy_fingerprint,
                payload={"loop": loop_detection.model_dump(mode="json")},
                created_at=timestamp,
            )
        )
        storage.json("replay.json", storage.replay())
        task_store.record_agentic_run(root, resumed)
        return {
            "run": resumed.model_dump(mode="json"),
            "artifacts": [],
            "status": "BLOCKED",
            "resumed": True,
            "reused_invocations": len(previous.invocation_ids),
            "gaps": (gap,),
            "loop": loop_detection.model_dump(mode="json"),
            "run_dir": str(storage.directory),
        }
    selected = tuple(
        by_name[step.name]
        for step in ready
        if step.name in by_name
        and step.name
        in {
            name
            for name in (
                routing_plan.primary,
                *routing_plan.parallel,
                *routing_plan.reviewers,
                routing_plan.critic,
                routing_plan.referee,
                *routing_plan.fallbacks,
            )
            if name is not None
        }
    )
    if not selected:
        raise ContractError(
            "AF-CAPABILITY-ELIGIBILITY",
            "field=capability; unlock=provide a resumable eligible capability",
        )
    step_map = {step.name: step for step in ready}
    invocations: list[AgentInvocation] = []
    for capability in selected:
        step = step_map[capability.name]
        control.start(run_id, step.step_id)
        invocations.append(
            AgentInvocation(
                invocation_id=stable_id("inv", {"run": run_id, "capability": capability.name}),
                run_id=run_id,
                agent=capability.agent,
                capability=capability.name,
                adapter=adapter.name,
                input_refs=spec.inputs,
                idempotency_key=step.idempotency_key,
                retry_count=step.attempts,
            )
        )

    async def worker(invocation: AgentInvocation) -> object:
        return await _authorized_invoke(
            adapter,
            AgentRequest(
                invocation_id=invocation.invocation_id,
                agent=invocation.agent,
                capability=invocation.capability,
                prompt=f"Resume API evolution for capability {invocation.capability}",
                output_contract="AgentArtifact/v1",
                authority_subject=by_name[invocation.capability].kind,
                delegated_from="api-orchestrator",
            ),
        )

    results = await run_bounded(
        tuple(invocations),
        worker,
        limit=policy.max_parallel_agents,
        timeout_seconds=policy.timeout_seconds,
        max_calls=max(0, policy.max_calls - control_run.calls_used),
        max_retries=policy.max_retries,
    )
    new_artifacts: list[AgentArtifact] = []
    errors: list[str] = []
    for result in results:
        step = step_map[result.invocation.capability]
        if result.error is not None or result.response is None:
            error = result.error or "invocation failed"
            errors.append(error)
            control.fail(run_id, step.step_id, error)
            continue
        try:
            payload = _json_payload(result.response)
        except (ContractError, ValueError) as exc:
            error = str(exc)
            errors.append(error)
            control.fail(run_id, step.step_id, error)
            continue
        gaps = validate_agent_payload(payload)
        if gaps:
            error = "; ".join(gaps)
            errors.extend(f"{result.invocation.capability}: {error}" for _ in [0])
            control.fail(run_id, step.step_id, error)
            continue
        artifact = AgentArtifact(
            artifact_id=stable_id(
                "artifact", {"run": run_id, "invocation": result.invocation.invocation_id}
            ),
            run_id=run_id,
            invocation_id=result.invocation.invocation_id,
            agent=result.invocation.agent,
            capability=result.invocation.capability,
            kind=ArtifactKind.SPECIALIST,
            schema_name="AgentArtifact/v1",
            payload=payload,
            evidence=_strings(payload, "facts"),
            assumptions=_strings(payload, "assumptions"),
            risks=_strings(payload, "risks"),
            unresolved=_strings(payload, "unresolved"),
            confidence=_confidence(payload),
            content_sha256=content_hash(payload),
        )
        control.complete(run_id, step.step_id, artifact.model_dump(mode="json"))
        storage.artifact(artifact)
        storage.event(
            TrajectoryEvent(
                event_id=stable_id(
                    "event",
                    {"run": run_id, "invocation": artifact.invocation_id, "event": "resume"},
                ),
                run_id=run_id,
                event="resume_checkpoint",
                actor="api-orchestrator",
                subject=artifact.invocation_id,
                payload={"artifact_id": artifact.artifact_id},
                created_at=timestamp,
            )
        )
        new_artifacts.append(artifact)
    artifact_ids = tuple(
        dict.fromkeys((*previous.artifact_ids, *(item.artifact_id for item in new_artifacts)))
    )
    final_status = "REVIEW" if errors or artifact_ids else "BLOCKED"
    resumed = previous.model_copy(
        update={
            "state": AgenticState.AWAITING_SUPERVISION
            if final_status == "REVIEW"
            else AgenticState.BLOCKED,
            "artifact_ids": artifact_ids,
            "gaps": tuple(sorted({*previous.gaps, *errors})),
            "final_status": final_status,
            "finished_at": timestamp,
            "run_digest": content_hash({"run": run_id, "artifacts": artifact_ids}),
        }
    )
    storage.save_run(resumed)
    calls_used = control.get(run_id).calls_used
    resume_checkpoint = build_checkpoint(
        run_id=run_id,
        task_id=task_id,
        plan=economy_plan,
        max_calls=policy.max_calls,
        calls_used=calls_used,
        stopped_at=checkpoint.stopped_at if checkpoint is not None else None,
        now=timestamp,
        resumes=(checkpoint.resumes + 1) if checkpoint is not None else 1,
        codes=tuple(note.split(":", 1)[0] for note in pin_notes),
    )
    save_checkpoint(storage.directory, resume_checkpoint)
    storage.json("replay.json", storage.replay())
    task_store.record_agentic_run(root, resumed)
    return {
        "run": resumed.model_dump(mode="json"),
        "artifacts": [item.model_dump(mode="json") for item in new_artifacts],
        "status": final_status,
        "resumed": True,
        "reused_invocations": len(previous.invocation_ids),
        "economy": {
            "checkpoint": resume_checkpoint.model_dump(mode="json"),
            "previous_calls_used": checkpoint.calls_used if checkpoint is not None else None,
            "diagnostics": list(pin_notes),
        },
        "run_dir": str(storage.directory),
    }
