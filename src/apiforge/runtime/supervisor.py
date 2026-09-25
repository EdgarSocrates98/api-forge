"""Deterministic supervisor for one TaskSpec-bound agentic run."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
from apiforge.contracts.base import ContractError
from apiforge.core.ids import stable_id
from apiforge.core.models import JsonValue
from apiforge.runtime.adapters import AgentRequest, ModelAdapter
from apiforge.runtime.control import ControlPlane
from apiforge.runtime.critic import critic_findings
from apiforge.runtime.guardrails import validate_agent_payload
from apiforge.runtime.policy import (
    load_policy,
    requires_critic,
    requires_human_gate,
    should_open_room,
)
from apiforge.runtime.registry import load_capabilities, load_profiles
from apiforge.runtime.review import build_runtime_review, review_task_spec
from apiforge.runtime.routing import (
    build_routing_request,
    load_routing_policy,
    route_capabilities,
)
from apiforge.runtime.scheduler import run_bounded
from apiforge.runtime.store import RunStore, content_hash
from apiforge.taskspec import store as task_store


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


async def execute_run(
    root: Path,
    task_id: str,
    *,
    adapter: ModelAdapter,
    policy_id: str = "local-ci-safe",
    now: str | None = None,
    requested_debate: bool = False,
) -> dict[str, object]:
    root = Path(root)
    spec = task_store.load(root, task_id)
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
            actor="api-agentic-orchestrator",
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
    routing = route_capabilities(
        capabilities_catalog,
        load_profiles(),
        build_routing_request(
            spec,
            policy_id=routing_policy.policy_id,
            available_evidence=("task_spec",),
        ),
        policy=routing_policy,
        scorecards=scorecards,
    )
    storage.save_routing(routing)
    storage.event(
        TrajectoryEvent(
            event_id=stable_id(
                "event", {"run": run_id, "event": "routing", "decision": routing.decision_id}
            ),
            run_id=run_id,
            event="routing_decision",
            actor="api-agentic-orchestrator",
            subject=routing.decision_id,
            payload={
                "selected": routing.selected,
                "fallback_order": routing.fallback_order,
                "unresolved": routing.unresolved,
            },
            created_at=timestamp,
        )
    )
    capabilities = tuple(capabilities_catalog[name] for name in routing.fallback_order)
    if not capabilities:
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
    invocation_ids = tuple(
        stable_id("inv", {"run": run_id, "capability": item.name}) for item in capabilities
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
        for invocation_id, item in zip(invocation_ids, capabilities, strict=True)
    )
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
        control.start(control_run.run_id, step.step_id)

    async def worker(invocation: AgentInvocation) -> object:
        request = AgentRequest(
            invocation_id=invocation.invocation_id,
            agent=invocation.agent,
            capability=invocation.capability,
            prompt=f"Review API evolution for capability {invocation.capability}",
            input_refs=invocation.input_refs,
            output_contract="AgentArtifact/v1",
        )
        return await adapter.invoke(request)

    results = await run_bounded(
        invocations,
        worker,
        limit=policy.max_parallel_agents,
        timeout_seconds=policy.timeout_seconds,
        max_calls=policy.max_calls,
        max_retries=policy.max_retries,
        parallelism=lambda ready, remaining: min(
            policy.max_parallel_agents,
            max(1, ready // 2)
            if spec.risk.value in {"sensitive", "external_mutation", "destructive", "irreversible"}
            else ready,
        ),
    )
    artifacts: list[AgentArtifact] = []
    errors: list[str] = []
    for result in results:
        control_step = control_steps[result.invocation.capability]
        if result.error is not None or result.response is None:
            errors.append(result.error or "invocation failed")
            control.fail(
                control_run.run_id, control_step.step_id, result.error or "invocation failed"
            )
            continue
        payload = _json_payload(result.response)
        guardrail_gaps = validate_agent_payload(payload)
        if guardrail_gaps:
            errors.extend(f"{result.invocation.capability}: {gap}" for gap in guardrail_gaps)
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
                actor="api-agentic-orchestrator",
                subject=result.invocation.invocation_id,
                payload={
                    "artifact_id": artifact.artifact_id,
                    "content_sha256": artifact.content_sha256,
                },
                created_at=timestamp,
            )
        )

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
            "gaps": tuple(sorted(set(errors + list(critic) + list(all_unresolved)))),
            "final_status": final_status,
            "finished_at": timestamp,
            "run_digest": content_hash(
                {"run": run_id, "artifacts": [item.model_dump(mode="json") for item in artifacts]}
            ),
        }
    )
    storage.save_run(run)
    storage.json(
        "summary.json",
        {
            "run_id": run_id,
            "critic_required": critic_required,
            "critic_findings": critic,
            "debate_reasons": reasons,
            "human_gate": needs_gate,
            "errors": errors,
        },
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
        "debate": {"opened": room, "reasons": reasons},
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
) -> dict[str, object]:
    root = Path(root)
    spec = task_store.load(root, task_id)
    timestamp = _now(now)
    policy = load_policy(policy_id)
    storage = RunStore(root, task_id, run_id)
    previous = storage.load_run()
    if previous is None:
        raise ContractError("AF-RUNTIME-NOT-FOUND", f"no runtime run {run_id!r}")
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
    routing = route_capabilities(
        capabilities,
        profiles,
        build_routing_request(
            spec,
            policy_id=routing_policy.policy_id,
            available_evidence=("task_spec",),
        ),
        policy=routing_policy,
        scorecards=scorecards,
    )
    storage.save_routing(routing)
    by_name = {item.name: item for item in capabilities.values()}
    selected = tuple(
        by_name[step.name]
        for step in ready
        if step.name in by_name and step.name in routing.fallback_order
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
        return await adapter.invoke(
            AgentRequest(
                invocation_id=invocation.invocation_id,
                agent=invocation.agent,
                capability=invocation.capability,
                prompt=f"Resume API evolution for capability {invocation.capability}",
                output_contract="AgentArtifact/v1",
            )
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
        payload = _json_payload(result.response)
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
                actor="api-agentic-orchestrator",
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
    storage.json("replay.json", storage.replay())
    task_store.record_agentic_run(root, resumed)
    return {
        "run": resumed.model_dump(mode="json"),
        "artifacts": [item.model_dump(mode="json") for item in new_artifacts],
        "status": final_status,
        "resumed": True,
        "reused_invocations": len(previous.invocation_ids),
        "run_dir": str(storage.directory),
    }
