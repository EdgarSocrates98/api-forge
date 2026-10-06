"""Economy replay (§77–78, §83–§85): re-decide stored runs under current policy.

A stored run keeps its routing decision (``routing.json``), economy plan
(``economy.json``), governance context, recovery receipts, model-route
shadow receipt, role-context plan, run record and trajectory events.
Replay strips the stored economy, rebuilds the pre-economy routing plan,
applies the current profile policy and compares: effective profile,
trimmed roles and — the invariant — whether any risk-required role would
now be missing. It then re-derives each persisted control-plane decision
(loop, model-route shadow, tool authorization, trust admission, recovery)
under the current policy files and reports ``same``/``changed``/
``unresolved``/``absent`` per decision — deterministic inputs only, never
LLM text (§85). Runs without a decision are reported ``unresolved``;
nothing is guessed.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_evals import ReplayDecision, ReplayReport, ReplayRun

_EXTRA_ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("run.json", "run"),
    ("governance-context.json", "governance"),
    ("recovery-receipts.json", "recovery_receipts"),
    ("model-route-shadow.json", "model_route_shadow"),
    ("role-context.json", "role_context"),
)


def _bundles_from_root(root: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    tasks = Path(root) / ".apiforge" / "tasks"
    if not tasks.is_dir():
        return
    for run_dir in sorted(tasks.glob("*/runs/*")):
        if not run_dir.is_dir():
            continue
        bundle: dict[str, Any] = {"task_id": run_dir.parent.parent.name}
        for name, key in (
            ("routing.json", "routing"),
            ("economy.json", "economy"),
            *_EXTRA_ARTIFACTS,
        ):
            path = run_dir / name
            if path.is_file():
                try:
                    bundle[key] = json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    bundle[key] = None
        events_path = run_dir / "events.jsonl"
        if events_path.is_file():
            events: list[dict[str, Any]] = []
            for line in events_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    events = []
                    break
            bundle["events"] = events
        yield f"{run_dir.parent.parent.name}/{run_dir.name}", bundle


def _bundles_from_corpus(corpus: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    for path in sorted(Path(corpus).glob("*.json")):
        yield path.stem, json.loads(path.read_text(encoding="utf-8"))


def _load_task(root: Path | None, bundle: Mapping[str, Any]) -> Any:
    from apiforge.contracts.task import TaskSpec

    if bundle.get("task") is not None:
        return TaskSpec.model_validate(bundle["task"])
    if root is not None:
        from apiforge.taskspec import store as task_store

        return task_store.load(root, str(bundle["task_id"]))
    return None


def _absent(name: str, detail: str) -> ReplayDecision:
    return ReplayDecision(name=name, status="absent", detail=detail)


def _replay_loop(bundle: Mapping[str, Any]) -> ReplayDecision:
    """§27 loop verdict re-derived from the persisted fingerprint stream."""
    from apiforge.contracts.agentic_governance import LoopAction
    from apiforge.core.policy import policy_descriptor
    from apiforge.governance.governor import GOVERNOR_POLICY
    from apiforge.governance.loop import check_loop, load_loop_policy

    governance = bundle.get("governance") or {}
    stored = governance.get("loop") if isinstance(governance, dict) else None
    if not isinstance(stored, dict):
        return _absent("loop", "run recorded no loop detection in governance-context.json")
    events = bundle.get("events") or ()
    history = tuple(
        str(payload["fingerprint"])
        for event in events
        if isinstance(event, dict)
        and event.get("event") == "strategy_selected"
        and isinstance((payload := event.get("payload")), dict)
        and isinstance(payload.get("fingerprint"), str)
    )
    policy_hash = policy_descriptor(GOVERNOR_POLICY, policy_id="loop")["policy_hash"]
    if not history:
        return ReplayDecision(
            name="loop",
            status="unresolved",
            stored=str(stored.get("blocked")),
            policy_hash=policy_hash,
            detail="strategy fingerprints not persisted in events.jsonl",
        )
    try:
        policy = load_loop_policy()
        recomputed = check_loop(
            history,
            window=int(policy["window"]),
            max_repeats=int(policy["max_repeats"]),
            blocked_action=cast("LoopAction", policy["blocked_action"]),
        )
    except (ValueError, ContractError) as exc:
        return ReplayDecision(
            name="loop",
            status="unresolved",
            stored=str(stored.get("blocked")),
            policy_hash=policy_hash,
            detail=f"current loop policy unreadable: {exc}",
        )
    same = bool(recomputed.blocked) == bool(
        stored.get("blocked")
    ) and recomputed.code == stored.get("code")
    return ReplayDecision(
        name="loop",
        status="same" if same else "changed",
        stored=f"blocked={stored.get('blocked')} code={stored.get('code')}",
        observed=f"blocked={recomputed.blocked} code={recomputed.code}",
        code=None if same else "AF-REPLAY-DECISION-CHANGED",
        policy_hash=policy_hash,
        detail="" if same else "current loop policy re-decides the fingerprint stream differently",
    )


def _replay_model_route_shadow(
    bundle: Mapping[str, Any], spec: Any, root: Path | None
) -> ReplayDecision:
    """§33 shadow verdict re-derived from the receipt's declared inputs."""
    from apiforge.contracts.model_routing import ModelEvaluation, ModelRouteShadowReceipt
    from apiforge.core.policy import policy_descriptor
    from apiforge.runtime.model_router import RULES, load_model_router_policy, route_model
    from apiforge.runtime.model_scorecard import aggregate_scorecards

    stored = bundle.get("model_route_shadow")
    if not isinstance(stored, dict):
        return _absent("model_route_shadow", "run recorded no model-route shadow receipt")
    policy_hash = policy_descriptor(RULES)["policy_hash"]
    try:
        receipt = ModelRouteShadowReceipt.model_validate(stored)
        rules = load_model_router_policy()
    except (ValidationError, ContractError, ValueError) as exc:
        return ReplayDecision(
            name="model_route_shadow",
            status="unresolved",
            policy_hash=policy_hash,
            detail=f"stored receipt or router policy unreadable: {exc}",
        )
    scorecards = None
    declared = next(
        (
            str(item).partition("=")[2]
            for item in getattr(spec, "inputs", ()) or ()
            if str(item).partition("=")[0] == "model_route_evaluations"
            and str(item).partition("=")[1]
        ),
        None,
    )
    if declared is not None and root is not None:
        resolved_root = Path(root).resolve()
        candidate = Path(declared)
        resolved = (
            candidate.resolve()
            if candidate.is_absolute()
            else (resolved_root / candidate).resolve()
        )
        if resolved != resolved_root and resolved_root not in resolved.parents:
            return ReplayDecision(
                name="model_route_shadow",
                status="unresolved",
                stored=(receipt.candidate.selected if receipt.candidate else None) or "",
                policy_hash=policy_hash,
                detail="declared evaluations path escapes the replay root (AF-PATH-OUTSIDE-ROOT)",
            )
        try:
            rows = [
                ModelEvaluation.model_validate(json.loads(line))
                for line in resolved.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            scorecards = aggregate_scorecards(rows)
        except (OSError, ValueError) as exc:
            return ReplayDecision(
                name="model_route_shadow",
                status="unresolved",
                stored=(receipt.candidate.selected if receipt.candidate else None) or "",
                policy_hash=policy_hash,
                detail=f"declared evaluations store unreadable: {exc}",
            )
    recomputed = route_model(receipt.inputs, rules["candidates"], scorecards, policy=rules)
    stored_selected = receipt.candidate.selected if receipt.candidate else None
    stored_eligible = sorted(
        f"{item.provider}/{item.model}"
        for item in (receipt.candidate.ranked if receipt.candidate else ())
        if item.eligible
    )
    observed_eligible = sorted(
        f"{item.provider}/{item.model}" for item in recomputed.ranked if item.eligible
    )
    same = recomputed.selected == stored_selected and stored_eligible == observed_eligible
    return ReplayDecision(
        name="model_route_shadow",
        status="same" if same else "changed",
        stored=str(stored_selected or "none"),
        observed=str(recomputed.selected or "none"),
        code=None if same else "AF-REPLAY-DECISION-CHANGED",
        policy_hash=policy_hash,
        detail="" if same else "router policy or scorecard drift changed the shadow verdict",
    )


def _replay_tool_authorization(bundle: Mapping[str, Any]) -> ReplayDecision:
    """§43 boundary grant re-derived; per-invocation tool grants are named
    honestly — the run record persists ids and gaps, not request tool names."""
    from apiforge.core.policy import policy_descriptor
    from apiforge.trust.tools import TOOL_RISK_FILE, authorize, load_tool_risk

    run = bundle.get("run")
    if not isinstance(run, dict):
        return _absent("tool_authorization", "run.json not persisted for this bundle")
    policy_hash = policy_descriptor(TOOL_RISK_FILE)["policy_hash"]
    try:
        profiles, permissions = load_tool_risk()
        boundary = authorize(
            "api-orchestrator", "agent-invocation", profiles=profiles, permissions=permissions
        )
    except (ContractError, ValueError) as exc:
        return ReplayDecision(
            name="tool_authorization",
            status="unresolved",
            policy_hash=policy_hash,
            detail=f"tool-risk policy unreadable: {exc}",
        )
    gaps = [str(gap) for gap in run.get("gaps") or ()]
    tool_denials = [gap for gap in gaps if gap.startswith(("AF-TOOL", "AF-MCP"))]
    proceeded = bool(run.get("invocation_ids")) or bool(run.get("artifact_ids"))
    stored = "denied" if (tool_denials and not proceeded) else "allowed"
    observed = "allowed" if boundary.decision == "allow" else "denied"
    same = stored == observed
    return ReplayDecision(
        name="tool_authorization",
        status="same" if same else "changed",
        stored=stored,
        observed=observed,
        code=None if same else "AF-REPLAY-DECISION-CHANGED",
        policy_hash=policy_hash,
        detail=(
            "" if same else "current tool-risk policy re-decides the adapter boundary differently"
        )
        + ("; per-invocation tool grants are not persisted" if tool_denials and proceeded else ""),
    )


def _replay_trust_admission(bundle: Mapping[str, Any]) -> ReplayDecision:
    """§8/§39 admitted trust units re-checked against the current role policy."""
    from apiforge.context.role_policy import policy_for
    from apiforge.contracts.selective import RoleContextPlan
    from apiforge.core.policy import policy_descriptor
    from apiforge.runtime.role_context import ROLE_FILE, load_role_policy
    from apiforge.trust.propagation import TRUST_ORDER

    plan = bundle.get("role_context")
    if not isinstance(plan, dict):
        return _absent("trust_admission", "role-context.json not persisted for this bundle")
    policy_hash = policy_descriptor(ROLE_FILE)["policy_hash"]
    try:
        stored_plan = RoleContextPlan.model_validate(plan)
        policies = load_role_policy()["policies"]
    except (ValidationError, ContractError, ValueError) as exc:
        return ReplayDecision(
            name="trust_admission",
            status="unresolved",
            policy_hash=policy_hash,
            detail=f"stored plan or role policy unreadable: {exc}",
        )
    violations: list[str] = []
    admitted = 0
    for row in stored_plan.roles:
        policy = policy_for(policies, row.role)
        floor = TRUST_ORDER.get(policy.trust_floor) if policy.trust_floor else None
        denied = set(policy.denied_taints)
        for unit in row.trust_units:
            admitted += 1
            if floor is not None and TRUST_ORDER.get(unit.trust_level, 0) < floor:
                violations.append(
                    f"{row.role}:{unit.subject} level={unit.trust_level} < floor {policy.trust_floor}"
                )
            if denied & set(unit.taint):
                violations.append(
                    f"{row.role}:{unit.subject} taint={sorted(denied & set(unit.taint))} denied"
                )
    same = not violations
    return ReplayDecision(
        name="trust_admission",
        status="same" if same else "changed",
        stored=f"admitted={admitted}",
        observed=f"admitted={admitted} violations={len(violations)}",
        code=None if same else "AF-REPLAY-DECISION-CHANGED",
        policy_hash=policy_hash,
        detail="" if same else "; ".join(sorted(set(violations))[:5]),
    )


def _replay_recovery(bundle: Mapping[str, Any]) -> ReplayDecision:
    """§26 recovery verdicts re-derived per stored failure class + attempt."""
    from apiforge.core.policy import policy_descriptor
    from apiforge.governance.recovery import RECOVERY_POLICY, decide_recovery

    receipts = bundle.get("recovery_receipts")
    if not receipts:
        return _absent("recovery", "run recorded no recovery receipts")
    policy_hash = policy_descriptor(RECOVERY_POLICY)["policy_hash"]
    diffs: list[str] = []
    checked = 0
    rows = receipts if isinstance(receipts, list) else ()
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        checked += 1
        try:
            recomputed = decide_recovery(str(raw["failure_class"]), int(raw.get("attempt", 0)))
        except (ContractError, ValueError, KeyError) as exc:
            diffs.append(f"{raw.get('capability')}: recompute failed {exc}")
            continue
        if recomputed.decision != raw.get("decision"):
            diffs.append(
                f"{raw.get('capability')}: stored={raw.get('decision')} "
                f"observed={recomputed.decision}"
            )
    if not checked:
        return ReplayDecision(
            name="recovery",
            status="unresolved",
            policy_hash=policy_hash,
            detail="recovery-receipts.json present but no receipt could be parsed",
        )
    same = not diffs
    return ReplayDecision(
        name="recovery",
        status="same" if same else "changed",
        stored=f"receipts={checked}",
        observed=f"receipts={checked} mismatches={len(diffs)}",
        code=None if same else "AF-REPLAY-DECISION-CHANGED",
        policy_hash=policy_hash,
        detail="" if same else "; ".join(diffs[:5]),
    )


def _replay_decisions(
    bundle: Mapping[str, Any], spec: Any, root: Path | None
) -> tuple[ReplayDecision, ...]:
    """§83/§87 decision chain, replayed in control-plane order."""
    return (
        _replay_loop(bundle),
        _replay_model_route_shadow(bundle, spec, root),
        _replay_tool_authorization(bundle),
        _replay_trust_admission(bundle),
        _replay_recovery(bundle),
    )


def replay_bundle(
    name: str, bundle: Mapping[str, Any], *, profile: str | None = None, root: Path | None = None
) -> ReplayRun:
    from apiforge.contracts.economy import EconomyPlan
    from apiforge.contracts.routing import RoutingDecision
    from apiforge.runtime.economy import (
        apply_economy,
        build_economy_plan,
        load_economy_config,
        role_kinds,
    )
    from apiforge.runtime.registry import load_capabilities
    from apiforge.runtime.routing import build_routing_plan, load_routing_policy

    if "routing" not in bundle or "economy" not in bundle:
        return ReplayRun(
            run=name,
            profile=profile or "",
            status="unresolved",
            reason="AF-REPLAY-RUN-INCOMPLETE: stored run lacks routing.json or economy.json",
            decisions=_replay_decisions(bundle, None, root),
        )
    try:
        decision = RoutingDecision.model_validate(bundle["routing"]).model_copy(
            update={"economy": None}
        )
        stored = EconomyPlan.model_validate(bundle["economy"])
        spec = _load_task(root, bundle)
    except (ValidationError, OSError, ValueError) as exc:
        return ReplayRun(
            run=name,
            profile=profile or "",
            status="unresolved",
            reason=f"AF-REPLAY-RUN-INCOMPLETE: {exc}",
            decisions=_replay_decisions(bundle, None, root),
        )
    if spec is None:
        return ReplayRun(
            run=name,
            profile=profile or "",
            status="unresolved",
            reason="AF-REPLAY-RUN-INCOMPLETE: task spec unavailable",
            decisions=_replay_decisions(bundle, None, root),
        )
    catalog = load_capabilities()
    kinds = {key: item.kind for key, item in catalog.items()}
    selected = profile or stored.requested
    plan = build_routing_plan(decision, catalog, policy=load_routing_policy())
    economy = build_economy_plan(
        decision, spec, flag=selected, manifest=None, config=load_economy_config()
    )
    kept, economy = apply_economy(plan, economy, decision, kinds)
    removed = tuple(sorted(set(economy.minimum_roles) - role_kinds(kept, kinds)))
    same = (
        economy.effective == stored.effective
        and tuple(economy.trimmed_roles) == tuple(stored.trimmed_roles)
        and not removed
    )
    return ReplayRun(
        run=name,
        profile=selected,
        status="same" if same else "changed",
        removed_required_roles=removed,
        trimmed_before=tuple(stored.trimmed_roles),
        trimmed_after=tuple(economy.trimmed_roles),
        effective_before=stored.effective,
        effective_after=economy.effective,
        reason="" if same else "policy or profile changes the plan",
        decisions=_replay_decisions(bundle, spec, root),
    )


def replay(
    *, root: Path | None = None, corpus: Path | None = None, profile: str | None = None
) -> ReplayReport:
    source = (
        _bundles_from_corpus(Path(corpus))
        if corpus is not None
        else _bundles_from_root(Path(root or "."))
    )
    runs = tuple(replay_bundle(name, bundle, profile=profile, root=root) for name, bundle in source)
    removed = sum(len(item.removed_required_roles) for item in runs)
    decisions = [decision for item in runs for decision in item.decisions]
    policies = {
        decision.name: str(decision.policy_hash) for decision in decisions if decision.policy_hash
    }
    return ReplayReport(
        runs=runs,
        changed=sum(item.status == "changed" for item in runs),
        unresolved=sum(item.status == "unresolved" for item in runs),
        removed_required_roles=removed,
        decisions_changed=sum(1 for decision in decisions if decision.status == "changed"),
        decisions_unresolved=sum(
            1 for decision in decisions if decision.status in {"unresolved", "absent"}
        ),
        policies=policies,
        passed=removed == 0,
    )


__all__ = ["replay", "replay_bundle"]
