"""Per-role context (§86–87): one shared capsule, each role gets only its subset.

The planner builds a single ContextCapsule for the TaskSpec target (``target=``
or ``graph_target=operation:...`` inputs) and gives each invocation the refs
its context class allows, capped at its share of its class pool: ``share x envelope.context_bytes`` is the
*total* for every instance of the class, so the plan never exceeds the envelope.
Without a target or case the roles get no capsule refs and the plan says so —
it never silently falls back to shipping the whole repository.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextCapsule, ContextRef
from apiforge.contracts.economy import CostVector, LedgerRef, RunLedgerEntry
from apiforge.contracts.selective import RoleContext, RoleContextPlan

ROLE_FILE = Path(__file__).resolve().parents[1] / "rules" / "role_context.yaml"
KINDS = ("specialist", "reviewer", "critic", "referee")


@lru_cache(maxsize=2)
def load_role_policy(path: Path = ROLE_FILE) -> dict[str, Any]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError("AF-ROLE-CONTEXT-POLICY", f"{path}: {exc}") from exc
    classes = raw.get("classes") if isinstance(raw, dict) else None
    roles = raw.get("roles") if isinstance(raw, dict) else None
    if (
        raw.get("schema") not in ("apiforge/role-context/v1", "apiforge/role-context/v2")
        or not isinstance(classes, dict)
        or not isinstance(roles, dict)
        or set(roles) != set(KINDS)
        or any(roles[kind] not in classes for kind in KINDS)
    ):
        raise ContractError(
            "AF-ROLE-CONTEXT-POLICY", f"{path} must map {list(KINDS)} to declared classes"
        )
    total = sum(float(item.get("share", 0)) for item in classes.values())
    if total > 1.0 + 1e-9:
        raise ContractError("AF-ROLE-CONTEXT-POLICY", f"class shares sum to {total} > 1.0")
    from apiforge.context.role_policy import parse_policies

    policies = parse_policies(raw.get("policies"), path=str(path))
    unknown = set(policies) - set(KINDS)
    if unknown:
        raise ContractError(
            "AF-ROLE-CONTEXT-POLICY", f"{path} policies name unknown roles {sorted(unknown)}"
        )
    return {"classes": classes, "roles": roles, "policies": policies}


def task_target(spec: Any) -> tuple[str | None, str | None]:
    """(target, case_dir) declared by the TaskSpec inputs, if any."""
    target: str | None = None
    case: str | None = None
    for item in spec.inputs:
        key, sep, value = item.partition("=")
        if not sep:
            continue
        if key == "target":
            target = value
        elif key == "graph_target" and value.startswith("operation:") and target is None:
            target = value.removeprefix("operation:")
        elif key == "case":
            case = value
    return target, case


def _capsule(
    root: Path, target: str | None, case: str | None, budget: int, run_id: str
) -> tuple[ContextCapsule | None, list[str]]:
    if target is None:
        return None, ["capsule-unavailable:no-target"]
    from apiforge.context.gateway.capsule import build_capsule

    case_dir = Path(case) if case else None
    if case_dir is not None and not case_dir.is_absolute():
        case_dir = root / case_dir
    try:
        capsule = build_capsule(
            root,
            target,
            case_dir=case_dir,
            budget_bytes=budget,
            run_id=run_id,
            verb="runtime role-context",
        )
    except ContractError as exc:
        return None, [f"capsule-unavailable:{exc.code}"]
    notes = [f"capsule-{capsule.status}"] if capsule.status != "ready" else []
    notes.extend(f"capsule:{item}" for item in capsule.unresolved)
    return capsule, notes


def plan_roles(
    root: Path,
    spec: Any,
    roles: Iterable[tuple[str, str]],
    *,
    context_bytes: int,
    run_id: str,
    artifacts: Mapping[str, str] | None = None,
    frameworks: Iterable[str] = (),
) -> RoleContextPlan:
    """``roles`` is ``(capability, kind)``; ``artifacts`` maps capability → artifact id."""
    from apiforge.knowledge.selector import select_expertise
    from apiforge.runtime.prompting import prefix_for

    policy = load_role_policy()
    target, case = task_target(spec)
    capsule, unresolved = _capsule(Path(root), target, case, context_bytes, run_id)
    refs: tuple[ContextRef, ...] = capsule.refs if capsule is not None else ()
    detected = tuple(frameworks)
    if capsule is not None and not detected:
        found = capsule.fingerprint.get("frameworks")
        detected = tuple(str(item) for item in found) if isinstance(found, list | tuple) else ()
    produced = dict(artifacts or {})
    rows: list[RoleContext] = []
    resolved = [
        (capability, raw_kind if raw_kind in KINDS else "specialist")
        for capability, raw_kind in roles
    ]
    members: dict[str, int] = {}
    for _, kind in resolved:
        cls = str(policy["roles"][kind])
        members[cls] = members.get(cls, 0) + 1
    seen: dict[str, int] = {}
    from apiforge.context.role_policy import (
        filter_refs,
        order_required_first,
        policy_for,
        required_missing,
    )

    role_policies: dict[str, Any] = policy.get("policies") or {}
    for capability, kind in resolved:
        cls = str(policy["roles"][kind])
        spec_cls = policy["classes"][cls]
        pool = int(float(spec_cls.get("share", 0)) * context_bytes)
        index = seen.get(cls, 0)
        seen[cls] = index + 1
        budget = pool // members[cls] + (pool % members[cls] if index == 0 else 0)
        row_policy = policy_for(role_policies, kind)
        if row_policy.max_context_bytes is not None:
            budget = min(budget, row_policy.max_context_bytes)
        allowed = set(spec_cls.get("kinds") or ())
        kept: list[ContextRef] = []
        trimmed: list[str] = []
        used = 0
        eligible = [ref for ref in refs if ref.kind in allowed]
        eligible, denied, deny_notes = filter_refs(row_policy, eligible)
        trimmed.extend(denied)
        unresolved.extend(deny_notes)
        eligible = order_required_first(row_policy, eligible)
        over_budget = 0
        for ref in eligible:
            if used + ref.size_bytes > budget:
                trimmed.append(ref.uri)
                over_budget += 1
                continue
            kept.append(ref)
            used += ref.size_bytes
        missing = required_missing(row_policy, eligible, kept)
        if missing:
            unresolved.append(
                f"AF-ROLE-CONTEXT-REQUIRED: field=required_kinds; role={capability}; "
                f"missing={missing}; unlock=widen the role budget or lower other kinds "
                "so required refs always fit"
            )
        if over_budget:
            unresolved.append(
                f"AF-ROLE-CONTEXT-BUDGET: field=context_bytes; role={capability}; "
                f"unlock=raise the profile to widen context ({over_budget} refs trimmed)"
            )
        artifact_refs = (
            tuple(
                f"artifact:{artifact}"
                for name, artifact in sorted(produced.items())
                if name != capability
            )
            if spec_cls.get("artifacts")
            else ()
        )
        expertise = select_expertise(spec.outcome, capability=capability, frameworks=detected)
        rows.append(
            RoleContext(
                role=kind,  # type: ignore[arg-type]
                capability=capability,
                context_class=cls,  # type: ignore[arg-type]
                refs=tuple(ref.uri for ref in kept),
                artifact_refs=artifact_refs,
                expertise=tuple(item.pack_id for item in expertise.selected),
                bytes=used,
                budget_bytes=budget,
                pool_bytes=pool,
                trimmed=tuple(trimmed),
                prompt_prefix_sha256=hashlib.sha256(
                    prefix_for(
                        root, capability, (item.pack_id for item in expertise.selected)
                    ).encode("utf-8")
                ).hexdigest(),
            )
        )
    full = sum(ref.size_bytes for ref in refs)
    return RoleContextPlan(
        run_id=run_id,
        target=target,
        capsule_id=capsule.capsule_id if capsule is not None else None,
        context_bytes=context_bytes,
        roles=tuple(rows),
        total_bytes=sum(row.bytes for row in rows),
        naive_bytes=full * len(rows),
        unresolved=tuple(sorted(set(unresolved))),
    )


def record(root: Path, plan: RoleContextPlan) -> tuple[str, ...]:
    """Attribute role bytes in the run ledger (payload_bytes stays 0).

    Rows are auditable: a row that cannot be persisted comes back as an
    ``AF-ECONOMY-LEDGER-PERSIST`` note for the run's economy gaps.
    """
    from apiforge.economy import run_ledger

    lost: list[str] = []
    for row in plan.roles:
        persisted = run_ledger.append(
            Path(root),
            RunLedgerEntry(
                run_id=plan.run_id,
                verb=f"runtime role:{row.role}",
                source="envelope",
                cost=CostVector(context_bytes=row.bytes),
                refs=tuple(
                    LedgerRef(
                        uri=uri,
                        label=row.capability,
                        provenance=f"role-context:{row.context_class}",
                        size_bytes=0,
                    )
                    for uri in row.refs
                ),
            ),
            auditable=True,
        )
        if not persisted:
            lost.append(
                f"{run_ledger.PERSIST_FAILURE}: field=ledger; role={row.capability}; "
                "unlock=make .apiforge writable and re-run; the role bytes were not recorded"
            )
    return tuple(lost)


def summary(plan: RoleContextPlan) -> dict[str, object]:
    return {
        "capsule_id": plan.capsule_id,
        "target": plan.target,
        "bytes_by_role": {row.capability: row.bytes for row in plan.roles},
        "total_bytes": plan.total_bytes,
        "naive_bytes": plan.naive_bytes,
        "unresolved": list(plan.unresolved),
    }


__all__ = ["load_role_policy", "plan_roles", "record", "summary", "task_target"]
