"""Deterministic supervisor for one TaskSpec-bound agentic run."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast, get_args

from pydantic import TypeAdapter

from apiforge.capabilities.scorecard import load_scorecards
from apiforge.contracts.agentic import (
    AgentArtifact,
    AgentCapabilityProfile,
    AgenticRun,
    AgenticState,
    AgentInvocation,
    AgentScorecard,
    ArtifactKind,
    TrajectoryEvent,
)
from apiforge.contracts.agentic_governance import (
    GovernorInputs,
    LoopAction,
    LoopDetection,
    RecoveryDecision,
    RecoveryOutcome,
    RecoveryOwner,
    RecoveryReceipt,
    RunGovernanceContext,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import EconomyPlan, LadderStep
from apiforge.contracts.graph import GraphEdge, GraphExport, GraphNode
from apiforge.contracts.routing import (
    RoutingDecision,
    RoutingPlan,
    RoutingPolicy,
    RoutingRequest,
)
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
from apiforge.runtime.control import ControlPlane, ControlStep
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
from apiforge.runtime.registry import Capability, load_capabilities, load_profiles
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
from apiforge.runtime.scheduler import InvocationResult, run_bounded
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


# One observed failure plus its canonical scheduler decision.
_RecoveryEvent = tuple[str, str, RecoveryDecision]

_RECOVERY_HUMAN_REASON = "recovery_escalation"


def _build_artifact(
    result: InvocationResult,
    *,
    run_id: str,
) -> tuple[AgentArtifact | None, str | None, RecoveryDecision | None]:
    """Turn a successful invocation response into an artifact, or return the
    governed failure for a post-invocation payload gap (first classification
    point — the scheduler never saw this error)."""
    try:
        payload = _json_payload(result.response)
    except (ContractError, ValueError) as exc:
        error = str(exc)
        return None, error, _recovery_for_error(error)
    guardrail_gaps = validate_agent_payload(payload)
    if guardrail_gaps:
        error = "; ".join(guardrail_gaps)
        return None, error, _recovery_for_error(error)
    return (
        AgentArtifact(
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
        ),
        None,
        None,
    )


@dataclass(slots=True)
class _ExecCtx:
    """Shared runtime surface for bounded recovery action execution."""

    storage: RunStore
    control: ControlPlane
    control_run_id: str
    control_steps: dict[str, ControlStep]
    capabilities: dict[str, Capability]
    adapter: ModelAdapter
    spec: Any
    run_id: str
    policy: Any
    worker: Any
    reserve: int
    timestamp: str
    artifacts: list[AgentArtifact] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    invocation_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class _RecoveryOutcome:
    receipts: list[RecoveryReceipt] = field(default_factory=list)
    gate_reasons: list[str] = field(default_factory=list)
    nested: list[_RecoveryEvent] = field(default_factory=list)


def _receipt(
    seq: int,
    ctx: _ExecCtx,
    capability: str | None,
    decision: RecoveryDecision,
    *,
    owner: RecoveryOwner,
    action_taken: str,
    outcome: RecoveryOutcome,
    code: str | None = None,
    evidence: tuple[str, ...] = (),
    unresolved: tuple[str, ...] = (),
    invocation_id: str | None = None,
) -> RecoveryReceipt:
    return RecoveryReceipt(
        receipt_id=stable_id(
            "receipt",
            {
                "run": ctx.run_id,
                "seq": seq,
                "capability": capability,
                "decision": decision.decision,
                "attempt": decision.attempt,
                "action": action_taken,
            },
        ),
        run_id=ctx.run_id,
        invocation_id=invocation_id,
        capability=capability,
        failure_class=decision.failure_class,
        decision=decision.decision,
        attempt=decision.attempt,
        owner=owner,
        action_taken=action_taken,
        outcome=outcome,
        code=code,
        evidence=evidence,
        unresolved=unresolved,
    )


def _model_route_inputs(
    spec: Any,
    routing: RoutingDecision,
    *,
    calls_remaining: int,
) -> tuple[Any, tuple[str, ...]]:
    """Derive §33 ``ModelRouteInputs`` strictly from declared run data.

    ``spec.inputs`` may declare ``model_route_<field>=<value>`` pairs; every
    field never declared stays ``None`` and lands in the decision's
    ``unresolved`` — nothing is inferred from task text. ``risk`` and
    ``task_complexity`` come from the sealed spec and the risk-complexity
    assessment; ``needs_structured_output`` is declared by the run's
    ``AgentArtifact/v1`` output contract unless the spec overrides it.
    """
    from apiforge.contracts.model_routing import (
        ModelRouteInputs,
        ModelTaskClass,
    )

    raw: dict[str, str] = {}
    for item in spec.inputs:
        key, sep, value = str(item).partition("=")
        if sep and key.startswith("model_route_"):
            raw[key] = value
    invalid: list[str] = []

    def _literal(field: str, allowed: tuple[str, ...]) -> str | None:
        value = raw.get(f"model_route_{field}")
        if value is None:
            return None
        if value not in allowed:
            invalid.append(field)
            return None
        return value

    def _number(field: str, parser: Any) -> Any:
        value = raw.get(f"model_route_{field}")
        if value is None:
            return None
        try:
            return parser(value)
        except (TypeError, ValueError):
            invalid.append(field)
            return None

    def _flag(field: str) -> bool | None:
        value = raw.get(f"model_route_{field}")
        if value is None:
            return None
        if value.strip().lower() in {"1", "true", "yes"}:
            return True
        if value.strip().lower() in {"0", "false", "no"}:
            return False
        invalid.append(field)
        return None

    structured = _flag("needs_structured_output")
    inputs = ModelRouteInputs(
        task_complexity=cast(Any, _governor_complexity(routing)),
        task_class=cast(
            ModelTaskClass | None,
            _literal("task_class", tuple(str(arg) for arg in get_args(ModelTaskClass))),
        ),
        risk=cast(Any, spec.risk.value),
        reasoning_needs=cast(Any, _literal("reasoning_needs", ("none", "light", "deep"))),
        context_size=_number("context_size", int),
        needs_tool_support=_flag("needs_tool_support"),
        needs_structured_output=True if structured is None else structured,
        max_latency_ms=_number("max_latency_ms", int),
        max_cost=_number("max_cost", float),
        budget_remaining={"calls": max(0, calls_remaining)},
        allow_challenger=bool(_flag("allow_challenger")),
    )
    return inputs, tuple(sorted(set(invalid)))


def _model_route_scorecards(
    root: Path, spec: Any, inputs: Any
) -> tuple[dict[tuple[str, str], Any] | dict[tuple[str, str, Any], Any] | None, str | None]:
    """Load §34 scorecards only when the spec declares an evaluations JSONL.

    The path must resolve inside ``root`` (``AF-PATH-OUTSIDE-ROOT``); when no
    store is declared the router runs with ``scorecards=None`` and marks the
    evidence missing rather than fabricating quality history.
    """
    from apiforge.contracts.model_routing import ModelEvaluation
    from apiforge.runtime.model_scorecard import aggregate_scorecards

    declared = next(
        (
            str(item).partition("=")[2]
            for item in spec.inputs
            if str(item).partition("=")[0] == "model_route_evaluations"
            and str(item).partition("=")[1]
        ),
        None,
    )
    if declared is None:
        return None, None
    resolved_root = root.resolve()
    path = Path(declared)
    resolved = path.resolve() if path.is_absolute() else (resolved_root / path).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        return None, "AF-PATH-OUTSIDE-ROOT"
    try:
        rows = [
            ModelEvaluation.model_validate(json.loads(line))
            for line in resolved.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, ValueError):
        return None, "AF-ROUTE-EVALUATIONS-INVALID"
    return aggregate_scorecards(rows), None


def _model_route_shadow(
    root: Path,
    spec: Any,
    routing: RoutingDecision,
    adapter: ModelAdapter,
    *,
    calls_used: int,
    max_calls: int,
    timestamp: str,
) -> Any:
    """§33 model routing as a shadow observer inside the governed run.

    The declared adapter/provider path remains authoritative: the candidate
    router is evaluated through ``route_model_shadow`` (which appends the
    §29 ``ShadowRecord`` to the control-plane ledger) and the verdict is
    returned as a ``ModelRouteShadowReceipt``. While ``control_plane.yaml``
    keeps ``model_routing`` in shadow mode the receipt can never alter
    execution — ``governing`` stays ``legacy``. A router/policy failure is
    recorded on the receipt instead of taking the run down.
    """
    from apiforge.contracts.model_routing import (
        ModelRouteDecision,
        ModelRouteShadowReceipt,
    )
    from apiforge.runtime.model_router import load_model_router_policy, route_model_shadow

    inputs, invalid = _model_route_inputs(spec, routing, calls_remaining=max_calls - calls_used)
    scorecards, scorecard_code = _model_route_scorecards(root, spec, inputs)
    legacy: dict[str, object] = {"selected": adapter.name, "source": "declared_adapter"}
    stamp = timestamp
    if scorecard_code is not None:
        invalid = tuple(sorted(set(invalid) | {"model_route_evaluations"}))
    try:
        rules = load_model_router_policy()
        result = route_model_shadow(
            root,
            inputs,
            rules["candidates"],
            scorecards,
            legacy_decision=legacy,
            policy=rules,
            now=datetime.fromisoformat(timestamp),
        )
    except Exception as exc:  # noqa: BLE001 — the shadow observer never takes the run down
        code = getattr(exc, "code", None) or "AF-ROUTE-POLICY-INVALID"
        return ModelRouteShadowReceipt(
            inputs=inputs,
            legacy_decision=legacy,
            code=str(code),
            invalid_inputs=tuple(invalid),
            unresolved=tuple(sorted(set(invalid) | {"router_policy"})),
            recorded_at=stamp,
        )
    candidate = ModelRouteDecision.model_validate(result["candidate"])
    control = cast(dict[str, object], result["control"])
    unresolved = set(candidate.unresolved) | set(invalid)
    if scorecard_code is not None:
        unresolved.add(scorecard_code)
    return ModelRouteShadowReceipt(
        mode=cast(Any, control.get("mode")),
        governing=cast(Any, control.get("governing")),
        inputs=inputs,
        legacy_decision=legacy,
        candidate=candidate,
        control=control,
        code=candidate.code or scorecard_code,
        invalid_inputs=tuple(invalid),
        unresolved=tuple(sorted(unresolved)),
        recorded_at=stamp,
    )


def _calls_remaining(ctx: _ExecCtx) -> int:
    return int(
        max(
            0,
            ctx.policy.max_calls - ctx.control.get(ctx.control_run_id).calls_used - ctx.reserve,
        )
    )


async def _invoke_recovery_step(
    ctx: _ExecCtx,
    capability: str,
    *,
    kind: str,
) -> tuple[AgentArtifact | None, RecoveryDecision | None]:
    """Execute one recovery-invoked capability: authority check via the shared
    worker, bounded retries via the scheduler, accounting under ``kind``."""
    step = ctx.control_steps[capability]
    try:
        ctx.control.start(ctx.control_run_id, step.step_id, kind=kind)
    except ContractError as exc:
        return None, _recovery_for_error(f"{exc.code} {exc}")
    invocation = AgentInvocation(
        invocation_id=stable_id("inv", {"run": ctx.run_id, "capability": capability, "kind": kind}),
        run_id=ctx.run_id,
        agent=ctx.capabilities[capability].agent,
        capability=capability,
        adapter=ctx.adapter.name,
        dependencies=(),
        input_refs=ctx.spec.inputs,
        idempotency_key=step.idempotency_key,
        retry_count=step.attempts,
    )
    ctx.invocation_ids.append(invocation.invocation_id)
    try:
        results = await run_bounded(
            (invocation,),
            ctx.worker,
            limit=1,
            timeout_seconds=ctx.policy.timeout_seconds,
            max_calls=None,
            max_retries=ctx.policy.max_retries,
        )
    except ContractError as exc:
        return None, _recovery_for_error(f"{exc.code} {exc}")
    if not results:
        ctx.control.skip(
            ctx.control_run_id, step.step_id, "AF-CONTROL-BUDGET: no recovery call remained"
        )
        return None, _recovery_for_error("AF-CONTROL-BUDGET no recovery call remained")
    result = results[0]
    if result.error is not None or result.response is None:
        error = result.error or "recovery invocation failed"
        ctx.errors.append(f"{capability}: {error}")
        failed_run = ctx.control.fail(ctx.control_run_id, step.step_id, error)
        if next(item for item in failed_run.steps if item.name == capability).status == "pending":
            ctx.control.skip(ctx.control_run_id, step.step_id, f"AF-RECOVERY-STEP-FAILED: {error}")
        return None, result.recovery or _recovery_for_error(error)
    artifact, payload_error, decision = _build_artifact(result, run_id=ctx.run_id)
    if payload_error is not None:
        ctx.errors.append(f"{capability}: {payload_error}")
        ctx.control.fail(ctx.control_run_id, step.step_id, payload_error)
        return None, decision
    ctx.artifacts.append(cast(AgentArtifact, artifact))
    ctx.control.complete(
        ctx.control_run_id, step.step_id, cast(AgentArtifact, artifact).model_dump(mode="json")
    )
    ctx.storage.artifact(cast(AgentArtifact, artifact))
    ctx.storage.event(
        TrajectoryEvent(
            event_id=stable_id(
                "event",
                {"run": ctx.run_id, "invocation": invocation.invocation_id, "event": kind},
            ),
            run_id=ctx.run_id,
            event=f"recovery_{kind}_checkpoint",
            actor="api-orchestrator",
            subject=invocation.invocation_id,
            payload={
                "artifact_id": cast(AgentArtifact, artifact).artifact_id,
                "capability": capability,
            },
            created_at=ctx.timestamp,
        )
    )
    return cast(AgentArtifact, artifact), None


def _fallback_candidate(
    *,
    routing: RoutingDecision,
    ctx: _ExecCtx,
    failed_capability: str,
    exhausted: set[str],
) -> str | None:
    """Next declared, eligible fallback candidate for the failed capability.

    ``RoutingDecision.fallback_order`` is the ranked eligible order produced
    by routing; a recovery fallback consumes it in order rather than
    inventing a parallel pool. Kind compatibility is enforced so a specialist
    failure never yields a critic/referee substitute.
    """
    failed_kind = ctx.capabilities[failed_capability].kind
    compatible = (
        {"specialist", "fallback"} if failed_kind in {"specialist", "fallback"} else {failed_kind}
    )
    consumed = exhausted | {step.name for step in ctx.control.get(ctx.control_run_id).steps}
    for name in routing.fallback_order:
        capability = ctx.capabilities.get(name)
        if name not in consumed and capability is not None and capability.kind in compatible:
            return name
    return None


async def _execute_recovery(
    ctx: _ExecCtx,
    events: list[_RecoveryEvent],
    *,
    routing: RoutingDecision,
    routing_plan: RoutingPlan,
    routing_request: RoutingRequest,
    routing_policy: RoutingPolicy,
    profiles: dict[str, AgentCapabilityProfile],
    scorecards: tuple[AgentScorecard, ...] | list[AgentScorecard],
    fallbacks_attempted: set[str],
    fallback_budget: int,
    max_replans: int,
    graph_kwargs: dict[str, Any] | None = None,
) -> _RecoveryOutcome:
    """Execute the scheduler's terminal recovery decisions, once each.

    Ownership: scheduler-emitted terminal results never carry ``retry`` (the
    retry loop lives inside ``run_bounded``), so a ``retry`` reaching the
    supervisor is a post-invocation failure — executed once as an accounted
    ``recovery`` call. ``stop`` is terminal by definition; ``escalate``
    raises the ``recovery_escalation`` gate reason so policy decides review
    vs human gate; ``fallback`` consumes ``RoutingDecision.fallback_order``
    within the plan's declared ``max_fallbacks`` bound; ``replan`` re-routes
    excluding capabilities that already failed in this run. Recovery-invoked
    failures produce receipts marked ``skipped`` (``AF-GOV-RECOVERY-DEPTH``)
    instead of triggering a second recovery pass — depth is bounded at one.
    """
    outcome = _RecoveryOutcome()
    seq = 0
    replans_done = 0

    def escalate(
        capability: str | None,
        decision: RecoveryDecision,
        action: str,
        *,
        code: str | None = None,
        unresolved: tuple[str, ...] = (),
    ) -> None:
        nonlocal seq
        outcome.gate_reasons.append(_RECOVERY_HUMAN_REASON)
        outcome.receipts.append(
            _receipt(
                seq,
                ctx,
                capability,
                decision,
                owner="human",
                action_taken=action,
                outcome="executed",
                code=code,
                unresolved=unresolved or decision.unresolved,
            )
        )
        seq += 1

    failed_caps = {capability for capability, _, _ in events}
    snapshot = tuple(events)
    for capability, _error, decision in snapshot:
        action = decision.decision
        if action == "retry":
            # The scheduler executes retry decisions inside run_bounded; a
            # retry reaching the supervisor came from a post-invocation error
            # whose step is already terminal. Execute it once, accounted as a
            # recovery call rather than a disguised step restart.
            if _calls_remaining(ctx) <= 0:
                escalate(
                    capability,
                    decision,
                    "escalated:retry_no_budget",
                    code="AF-BUDGET-EXHAUSTED",
                    unresolved=(capability,),
                )
                continue
            try:
                ctx.control.record_call(ctx.control_run_id, "recovery")
            except ContractError:
                escalate(
                    capability,
                    decision,
                    "escalated:retry_no_budget",
                    code="AF-BUDGET-EXHAUSTED",
                    unresolved=(capability,),
                )
                continue
            invocation = AgentInvocation(
                invocation_id=stable_id(
                    "inv",
                    {"run": ctx.run_id, "capability": capability, "kind": "retry"},
                ),
                run_id=ctx.run_id,
                agent=ctx.capabilities[capability].agent,
                capability=capability,
                adapter=ctx.adapter.name,
                dependencies=(),
                input_refs=ctx.spec.inputs,
                retry_count=decision.attempt + 1,
            )
            ctx.invocation_ids.append(invocation.invocation_id)
            try:
                retry_results = await run_bounded(
                    (invocation,),
                    ctx.worker,
                    limit=1,
                    timeout_seconds=ctx.policy.timeout_seconds,
                    max_calls=None,
                    max_retries=0,
                )
            except ContractError as exc:
                escalate(
                    capability,
                    decision,
                    "escalated:retry_failed",
                    code=exc.code,
                    unresolved=(capability,),
                )
                continue
            retry_result = retry_results[0] if retry_results else None
            retry_decision = retry_result.recovery if retry_result is not None else None
            retry_artifact: AgentArtifact | None = None
            if (
                retry_result is not None
                and retry_result.error is None
                and retry_result.response is not None
            ):
                retry_artifact, payload_error, retry_decision = _build_artifact(
                    retry_result, run_id=ctx.run_id
                )
                if payload_error is not None:
                    ctx.errors.append(f"{capability}: {payload_error}")
                elif retry_artifact is not None:
                    ctx.artifacts.append(retry_artifact)
                    ctx.storage.artifact(retry_artifact)
            elif retry_result is not None:
                ctx.errors.append(
                    f"{capability}: {retry_result.error or 'retry invocation failed'}"
                )
            outcome.receipts.append(
                _receipt(
                    seq,
                    ctx,
                    capability,
                    decision,
                    owner="supervisor",
                    action_taken=f"retried:{capability}",
                    outcome="executed",
                    evidence=(
                        f"invocation:{invocation.invocation_id}",
                        "artifact:produced" if retry_artifact is not None else "artifact:none",
                    ),
                    invocation_id=invocation.invocation_id,
                )
            )
            seq += 1
            if retry_decision is not None and retry_artifact is None:
                outcome.nested.append((capability, "recovery retry failed", retry_decision))
            continue
        if action == "stop":
            outcome.receipts.append(
                _receipt(
                    seq,
                    ctx,
                    capability,
                    decision,
                    owner="none",
                    action_taken="stopped",
                    outcome="executed",
                    code=decision.code,
                    evidence=("terminal_no_calls",),
                )
            )
            seq += 1
            continue
        if action == "escalate":
            escalate(capability, decision, "escalated:human_gate", code=decision.code)
            continue
        if action == "fallback":
            if _calls_remaining(ctx) <= 0 or len(fallbacks_attempted) >= fallback_budget:
                escalate(
                    capability,
                    decision,
                    "escalated:no_fallback_budget",
                    code="AF-GOV-RECOVERY-NO-FALLBACK",
                    unresolved=(capability, "fallback_budget"),
                )
                continue
            candidate = _fallback_candidate(
                routing=routing,
                ctx=ctx,
                failed_capability=capability,
                exhausted=fallbacks_attempted,
            )
            if candidate is None:
                escalate(
                    capability,
                    decision,
                    "escalated:no_declared_fallback",
                    code="AF-GOV-RECOVERY-NO-FALLBACK",
                    unresolved=(capability,),
                )
                continue
            strategy: dict[str, JsonValue] = {
                "primary": candidate,
                "fallbacks": (),
                "execution_mode": "recovery_fallback",
                "parallel": 0,
            }
            loop = _record_strategy(ctx.storage, ctx.run_id, strategy, ctx.timestamp)
            if loop.blocked:
                escalate(
                    capability,
                    decision,
                    "escalated:loop_blocked",
                    code=loop.code or "AF-GOV-LOOP-DETECTED",
                    unresolved=(capability, "loop"),
                )
                continue
            if candidate not in ctx.control_steps:
                registered = {step.name: step for step in ctx.control.get(ctx.control_run_id).steps}
                if candidate not in registered:
                    ctx.control.add_steps(ctx.control_run_id, ((candidate, ()),))
                    registered = {
                        step.name: step for step in ctx.control.get(ctx.control_run_id).steps
                    }
                ctx.control_steps[candidate] = registered[candidate]
            fallbacks_attempted.add(candidate)
            calls_before = len(ctx.invocation_ids)
            artifact, nested_decision = await _invoke_recovery_step(ctx, candidate, kind="recovery")
            invocation_ref = (
                (f"invocation:{ctx.invocation_ids[-1]}",)
                if len(ctx.invocation_ids) > calls_before
                else ()
            )
            outcome.receipts.append(
                _receipt(
                    seq,
                    ctx,
                    capability,
                    decision,
                    owner="supervisor",
                    action_taken=f"fallback:{candidate}",
                    outcome="executed",
                    evidence=(
                        f"capability:{candidate}",
                        *invocation_ref,
                        *(("artifact:produced",) if artifact is not None else ("artifact:none",)),
                    ),
                )
            )
            if artifact is None and nested_decision is not None:
                outcome.nested.append((candidate, "recovery fallback failed", nested_decision))
            seq += 1
            continue
        if action == "replan":
            if replans_done >= max_replans or _calls_remaining(ctx) <= 0:
                escalate(
                    capability,
                    decision,
                    "escalated:replan_refused",
                    code="AF-GOV-RECOVERY-REPLAN-REFUSED",
                    unresolved=(capability, "max_replans"),
                )
                continue
            replans_done += 1
            replan_outcome = await _replan_once(
                ctx,
                routing_request=routing_request,
                routing_policy=routing_policy,
                profiles=profiles,
                scorecards=scorecards,
                exclude=set(failed_caps),
                graph_kwargs=graph_kwargs or {},
            )
            if replan_outcome is None:
                escalate(
                    capability,
                    decision,
                    "escalated:replan_empty",
                    code="AF-GOV-RECOVERY-REPLAN-REFUSED",
                    unresolved=(capability,),
                )
                continue
            new_decision, new_plan, executed, nested_failures = replan_outcome
            for name, nested in nested_failures:
                outcome.nested.append((name, "recovery replan step failed", nested))
            outcome.receipts.append(
                _receipt(
                    seq,
                    ctx,
                    capability,
                    decision,
                    owner="supervisor",
                    action_taken=f"replanned:{new_decision.decision_id}",
                    outcome="executed",
                    evidence=(
                        f"routing_decision:{new_decision.decision_id}",
                        f"plan:{new_plan.plan_id}",
                        *(f"invoked:{name}" for name in executed),
                    ),
                )
            )
            seq += 1
            continue
    # Depth bound: decisions emitted by recovery-invoked work are receipts
    # only — a second recovery pass is never spawned inside this executor.
    for capability, error, nested_decision in outcome.nested:
        outcome.receipts.append(
            _receipt(
                seq,
                ctx,
                capability,
                nested_decision,
                owner="supervisor",
                action_taken=f"observed_only:{nested_decision.decision}",
                outcome="skipped",
                code="AF-GOV-RECOVERY-DEPTH",
                unresolved=(capability,),
            )
        )
        seq += 1
    return outcome


async def _replan_once(
    ctx: _ExecCtx,
    *,
    routing_request: RoutingRequest,
    routing_policy: RoutingPolicy,
    profiles: dict[str, AgentCapabilityProfile],
    scorecards: tuple[AgentScorecard, ...] | list[AgentScorecard],
    exclude: set[str],
    graph_kwargs: dict[str, Any],
) -> (
    tuple[RoutingDecision, RoutingPlan, tuple[str, ...], list[tuple[str, RecoveryDecision]]] | None
):
    """Bounded replan: re-route with failed capabilities excluded, record the
    new strategy fingerprint for loop detection, then execute the plan's
    remaining primary/parallel names as governed recovery steps."""
    remaining = {
        name: capability for name, capability in ctx.capabilities.items() if name not in exclude
    }
    decision = route_capabilities(
        remaining,
        profiles,
        routing_request,
        policy=routing_policy,
        scorecards=tuple(scorecards),
        **graph_kwargs,
    )
    ctx.storage.save_routing(decision)
    plan = build_routing_plan(decision, remaining, policy=routing_policy)
    ctx.storage.save_routing_plan(plan)
    strategy = _strategy_payload(plan, ctx.policy)
    loop = _record_strategy(ctx.storage, ctx.run_id, strategy, ctx.timestamp)
    if loop.blocked:
        return None
    wanted = tuple(
        dict.fromkeys(name for name in (plan.primary, *plan.parallel) if name is not None)
    )
    fresh = tuple(
        name
        for name in wanted
        if name not in ctx.control_steps and name not in exclude and name in remaining
    )
    if not fresh:
        return None
    budgeted = fresh[: _calls_remaining(ctx)]
    if not budgeted:
        return None
    ctx.control.add_steps(ctx.control_run_id, tuple((name, ()) for name in budgeted))
    for name in budgeted:
        ctx.control_steps[name] = next(
            step for step in ctx.control.get(ctx.control_run_id).steps if step.name == name
        )
    executed: list[str] = []
    nested_failures: list[tuple[str, RecoveryDecision]] = []
    for name in budgeted:
        artifact, nested = await _invoke_recovery_step(ctx, name, kind="replan")
        if artifact is not None:
            executed.append(name)
        elif nested is not None:
            nested_failures.append((name, nested))
    return decision, plan, tuple(executed), nested_failures


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
    recovery_events: list[_RecoveryEvent] = []
    fallbacks_attempted: set[str] = set()
    for result in results:
        control_step = control_steps[result.invocation.capability]
        if result.error is not None or result.response is None:
            error = result.error or "invocation failed"
            errors.append(error)
            if result.recovery is not None:
                recovery_events.append((result.invocation.capability, error, result.recovery))
            elif result.invocation.error_code != "AF-RUNTIME-DEPENDENCY-FAILED":
                recovery_events.append(
                    (result.invocation.capability, error, _recovery_for_error(error))
                )
            control.fail(control_run.run_id, control_step.step_id, error)
            continue
        artifact, payload_error, decision = _build_artifact(result, run_id=run_id)
        if payload_error is not None:
            errors.append(f"{result.invocation.capability}: {payload_error}")
            if decision is not None:
                recovery_events.append((result.invocation.capability, payload_error, decision))
            control.fail(control_run.run_id, control_step.step_id, payload_error)
            continue
        artifact = cast(AgentArtifact, artifact)
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
                recovery_events.append((fallback, error, _recovery_for_error(error)))
                control.skip(
                    control_run.run_id,
                    fallback_step.step_id,
                    "AF-ROUTING-FALLBACK-BUDGET: no call budget remained",
                )
                continue
            fallbacks_attempted.add(fallback)
            fallback_result = fallback_results[0]
            if fallback_result.error is not None or fallback_result.response is None:
                error = fallback_result.error or "fallback invocation failed"
                errors.append(f"{fallback}: {error}")
                recovery_events.append(
                    (
                        fallback,
                        error,
                        fallback_result.recovery or _recovery_for_error(error),
                    )
                )
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
            artifact, payload_error, fallback_decision = _build_artifact(
                fallback_result, run_id=run_id
            )
            if payload_error is not None:
                errors.append(f"{fallback}: {payload_error}")
                if fallback_decision is not None:
                    recovery_events.append((fallback, payload_error, fallback_decision))
                failed_run = control.fail(control_run.run_id, fallback_step.step_id, payload_error)
                if (
                    next(item for item in failed_run.steps if item.name == fallback).status
                    == "pending"
                ):
                    control.skip(
                        control_run.run_id,
                        fallback_step.step_id,
                        f"AF-ROUTING-FALLBACK-INVALID: {payload_error}",
                    )
                continue
            artifact = cast(AgentArtifact, artifact)
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
    # every invocation failure; recovery_events was collected in error order
    # during processing, so the first entry governs the run's outcome. The
    # supervisor then executes each decision exactly once — replan, fallback,
    # escalate and stop are real runtime actions with persisted receipts, not
    # labels on a context object.
    recovery_ctx = _ExecCtx(
        storage=storage,
        control=control,
        control_run_id=control_run.run_id,
        control_steps=control_steps,
        capabilities=capabilities_catalog,
        adapter=adapter,
        spec=spec,
        run_id=run_id,
        policy=policy,
        worker=worker,
        reserve=reserve,
        timestamp=timestamp,
        artifacts=artifacts,
        errors=errors,
        invocation_ids=all_invocation_ids,
    )
    recovery_outcome = await _execute_recovery(
        recovery_ctx,
        recovery_events,
        routing=routing,
        routing_plan=routing_plan,
        routing_request=routing_request,
        routing_policy=routing_policy,
        profiles=load_profiles(),
        scorecards=scorecards,
        fallbacks_attempted=fallbacks_attempted,
        fallback_budget=routing_plan.max_fallbacks,
        max_replans=governor_decision.max_replans,
        graph_kwargs={
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges,
            "graph_snapshot": graph_snapshot,
        },
    )
    recovery_events.extend(recovery_outcome.nested)
    recovery_gate_reasons = recovery_outcome.gate_reasons
    recovery_receipts = recovery_outcome.receipts
    recovery_decisions = [decision for _, _, decision in recovery_events]
    if recovery_receipts:
        storage.json(
            "recovery-receipts.json",
            [receipt.model_dump(mode="json") for receipt in recovery_receipts],
        )
    recovery = recovery_decisions[0] if recovery_decisions else None
    # §33 model routing runs in shadow inside every governed run: the declared
    # adapter decision stays authoritative while the candidate router's verdict
    # is recorded through the §29 control plane and persisted as a receipt.
    model_route_receipt = _model_route_shadow(
        root,
        spec,
        routing,
        adapter,
        calls_used=control.get(control_run.run_id).calls_used,
        max_calls=policy.max_calls,
        timestamp=timestamp,
    )
    storage.json("model-route-shadow.json", model_route_receipt.model_dump(mode="json"))
    storage.event(
        TrajectoryEvent(
            event_id=stable_id("event", {"run": run_id, "event": "model_route_shadow"}),
            run_id=run_id,
            event="model_route_shadow",
            actor="api-orchestrator",
            subject=model_route_receipt.route,
            payload=model_route_receipt.model_dump(mode="json"),
            created_at=timestamp,
        )
    )
    governance_unresolved = set(governance_context.unresolved)
    governance_unresolved.update(model_route_receipt.unresolved)
    if model_route_receipt.code:
        governance_unresolved.add(model_route_receipt.code)
    for decision in recovery_decisions:
        governance_unresolved.update(decision.unresolved)
        if decision.code:
            governance_unresolved.add(decision.code)
    for receipt in recovery_receipts:
        governance_unresolved.update(receipt.unresolved)
        if receipt.code:
            governance_unresolved.add(receipt.code)
    governance_context = governance_context.model_copy(
        update={
            "recovery": recovery,
            "recoveries": tuple(recovery_decisions),
            "receipts": tuple(recovery_receipts),
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
                "recovery_receipts": tuple(receipt.receipt_id for receipt in recovery_receipts),
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
    gate_reasons = tuple(
        sorted(set(reasons + (("critic_findings",) if critic else ())) | set(recovery_gate_reasons))
    )
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
            "model_route_shadow": model_route_receipt.model_dump(mode="json"),
            "critic_required": critic_required,
            "critic_findings": critic,
            "debate_reasons": reasons,
            "human_gate": needs_gate,
            "recovery_receipts": [receipt.model_dump(mode="json") for receipt in recovery_receipts],
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
        "recovery_receipts": [receipt.model_dump(mode="json") for receipt in recovery_receipts],
        "role_context": role_summary(role_plan) if role_plan is not None else None,
        "shadow": shadow_decision.model_dump(mode="json") if shadow_decision is not None else None,
        "model_route_shadow": model_route_receipt.model_dump(mode="json"),
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
    # Recovery decisions observed during a resumed run follow the same
    # canonical path: scheduler decision first, supervisor classification
    # only for post-invocation payload gaps.
    recovery_events: list[_RecoveryEvent] = []
    for result in results:
        step = step_map[result.invocation.capability]
        if result.error is not None or result.response is None:
            error = result.error or "invocation failed"
            errors.append(error)
            if result.recovery is not None:
                recovery_events.append((result.invocation.capability, error, result.recovery))
            elif result.invocation.error_code != "AF-RUNTIME-DEPENDENCY-FAILED":
                recovery_events.append(
                    (result.invocation.capability, error, _recovery_for_error(error))
                )
            control.fail(run_id, step.step_id, error)
            continue
        artifact, payload_error, decision = _build_artifact(result, run_id=run_id)
        if payload_error is not None:
            errors.append(f"{result.invocation.capability}: {payload_error}")
            if decision is not None:
                recovery_events.append((result.invocation.capability, payload_error, decision))
            control.fail(run_id, step.step_id, payload_error)
            continue
        artifact = cast(AgentArtifact, artifact)
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
    recovery_ctx = _ExecCtx(
        storage=storage,
        control=control,
        control_run_id=run_id,
        control_steps=step_map,
        capabilities=capabilities,
        adapter=adapter,
        spec=spec,
        run_id=run_id,
        policy=policy,
        worker=worker,
        reserve=0,
        timestamp=timestamp,
        artifacts=new_artifacts,
        errors=errors,
        invocation_ids=[],
    )
    recovery_outcome = await _execute_recovery(
        recovery_ctx,
        recovery_events,
        routing=routing,
        routing_plan=routing_plan,
        routing_request=routing_request,
        routing_policy=routing_policy,
        profiles=profiles,
        scorecards=scorecards,
        fallbacks_attempted=set(),
        fallback_budget=routing_plan.max_fallbacks,
        max_replans=1,
        graph_kwargs={
            "graph_nodes": graph_nodes,
            "graph_edges": graph_edges,
            "graph_snapshot": graph_snapshot,
        },
    )
    recovery_events.extend(recovery_outcome.nested)
    if recovery_outcome.receipts:
        storage.json(
            "recovery-receipts.json",
            [receipt.model_dump(mode="json") for receipt in recovery_outcome.receipts],
        )
        storage.event(
            TrajectoryEvent(
                event_id=stable_id("event", {"run": run_id, "event": "recovery_actions"}),
                run_id=run_id,
                event="recovery_actions",
                actor="api-orchestrator",
                subject=run_id,
                payload={
                    "receipts": tuple(
                        receipt.model_dump(mode="json") for receipt in recovery_outcome.receipts
                    ),
                    "decisions": tuple(
                        decision.model_dump(mode="json") for _, _, decision in recovery_events
                    ),
                },
                created_at=timestamp,
            )
        )
        for receipt in recovery_outcome.receipts:
            if receipt.code is not None and receipt.outcome != "executed":
                errors.append(
                    f"{receipt.code}: field=recovery.{receipt.capability}; "
                    f"unlock={receipt.action_taken}"
                )
            if _RECOVERY_HUMAN_REASON in recovery_outcome.gate_reasons:
                errors.append(
                    "AF-GOV-RECOVERY-ESCALATION: field=recovery; "
                    "unlock=human review required before this run can close"
                )
                break
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
            "invocation_ids": tuple(
                dict.fromkeys(
                    (
                        *previous.invocation_ids,
                        *(item.invocation_id for item in invocations),
                        *recovery_ctx.invocation_ids,
                    )
                )
            ),
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
        "recovery_receipts": [
            receipt.model_dump(mode="json") for receipt in recovery_outcome.receipts
        ],
        "economy": {
            "checkpoint": resume_checkpoint.model_dump(mode="json"),
            "previous_calls_used": checkpoint.calls_used if checkpoint is not None else None,
            "diagnostics": list(pin_notes),
        },
        "run_dir": str(storage.directory),
    }
