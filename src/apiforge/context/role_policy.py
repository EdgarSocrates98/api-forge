"""RoleContext v2 policy enforcement (prompt §7).

Policies are data: they live in ``rules/role_context.yaml`` under the
``policies:`` mapping and are parsed into ``RoleContextPolicy`` contracts.
Enforcement is deterministic and deny-first where the policy declares a deny;
absent policy sections keep the permissive v1 behavior so existing plans and
eval fixtures are unchanged.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextRef, RefOrigin
from apiforge.contracts.context_quality import RoleContextPolicy, VisibilityLevel
from apiforge.contracts.trust import TrustUnit

#: Deterministic provenance rank — never a model-asserted trust score.
ORIGIN_RANK: dict[RefOrigin, int] = {
    "filesystem": 0,
    "knowledge": 1,
    "code": 2,
    "graph": 3,
    "contract": 4,
}

VISIBILITY_RANK: dict[VisibilityLevel, int] = {"none": 0, "summary": 1, "full": 2}


def parse_policies(raw: Any, *, path: str) -> dict[str, RoleContextPolicy]:
    """Parse the ``policies:`` yaml block into validated contracts."""
    if raw is None:
        return {}
    if not isinstance(raw, Mapping):
        raise ContractError(
            "AF-ROLE-CONTEXT-POLICY", f"{path}: policies must map roles to policy rows"
        )
    out: dict[str, RoleContextPolicy] = {}
    for role, spec in raw.items():
        if not isinstance(spec, Mapping):
            raise ContractError(
                "AF-ROLE-CONTEXT-POLICY", f"{path}: policies.{role} must be a mapping"
            )
        try:
            out[str(role)] = RoleContextPolicy(role=role, **dict(spec))
        except ValueError as exc:
            raise ContractError(
                "AF-ROLE-CONTEXT-POLICY", f"{path}: policies.{role}: {exc}"
            ) from exc
    return out


def default_policy(role: str) -> RoleContextPolicy:
    """The permissive v1 default: everything allowed, no extra limits."""
    return RoleContextPolicy(role=role)  # type: ignore[arg-type]


def policy_for(policies: Mapping[str, RoleContextPolicy], role: str) -> RoleContextPolicy:
    return policies.get(role, default_policy(role))


def filter_refs(
    policy: RoleContextPolicy, refs: list[ContextRef]
) -> tuple[list[ContextRef], list[str], list[str]]:
    """Apply denied kinds and origin-rank floors. Returns (kept, trimmed, notes)."""
    kept: list[ContextRef] = []
    trimmed: list[str] = []
    notes: list[str] = []
    denied = set(policy.denied_kinds)
    floor = ORIGIN_RANK.get(policy.minimum_origin_rank) if policy.minimum_origin_rank else None
    for ref in refs:
        if ref.kind in denied:
            trimmed.append(ref.uri)
            notes.append(
                f"AF-ROLE-CONTEXT-DENIED: field=kind; role={policy.role}; "
                f"kind={ref.kind}; unlock=grant the kind in rules/role_context.yaml "
                "or route the evidence through an allowed kind"
            )
            continue
        if floor is not None and ORIGIN_RANK.get(ref.origin, -1) < floor:
            trimmed.append(ref.uri)
            notes.append(
                f"AF-ROLE-CONTEXT-TRUST: field=origin; role={policy.role}; "
                f"origin={ref.origin} below {policy.minimum_origin_rank}; "
                "unlock=attest the ref from a higher-trust origin"
            )
            continue
        kept.append(ref)
    return kept, trimmed, notes


def admit_refs(
    policy: RoleContextPolicy, refs: list[ContextRef]
) -> tuple[list[ContextRef], list[str], list[str], tuple[TrustUnit, ...]]:
    """§8/§39 admission: filter_refs verdicts plus the declared trust posture.

    Every kept ref carries its annotated ``TrustUnit``; a declared
    ``trust_floor`` trims units below it (``AF-TRUST-FLOOR``) and
    ``denied_taints`` trims tainted units (``AF-TRUST-TAINT-DENIED``) —
    denied context is named in ``notes``, never silently dropped.
    """
    from apiforge.trust.plane import annotate_ref
    from apiforge.trust.propagation import TRUST_ORDER

    kept, trimmed, notes = filter_refs(policy, refs)
    floor = TRUST_ORDER.get(policy.trust_floor) if policy.trust_floor else None
    denied_taints = set(policy.denied_taints)
    units: list[TrustUnit] = []
    admitted: list[ContextRef] = []
    for ref in kept:
        unit = annotate_ref(ref).trust
        if floor is not None and TRUST_ORDER.get(unit.trust_level, 0) < floor:
            trimmed.append(ref.uri)
            notes.append(
                f"AF-TRUST-FLOOR: field=trust_level; role={policy.role}; "
                f"level={unit.trust_level} below {policy.trust_floor}; "
                "unlock=attest the ref from a higher-trust origin or lower the floor"
            )
            continue
        if denied_taints & set(unit.taint):
            trimmed.append(ref.uri)
            notes.append(
                f"AF-TRUST-TAINT-DENIED: field=taint; role={policy.role}; "
                f"taint={sorted(denied_taints & set(unit.taint))}; "
                "unlock=run a governed_verification propagation with evidence "
                "to reduce the declared taint"
            )
            continue
        units.append(unit)
        admitted.append(ref)
    return admitted, trimmed, notes, tuple(units)


def order_required_first(policy: RoleContextPolicy, refs: list[ContextRef]) -> list[ContextRef]:
    """Required kinds are delivered first inside the role's budget."""
    required = set(policy.required_kinds)
    if not required:
        return refs
    return sorted(refs, key=lambda ref: ref.kind not in required)


def required_missing(
    policy: RoleContextPolicy, eligible: list[ContextRef], kept: list[ContextRef]
) -> list[str]:
    """Kinds the policy requires that *were* in the capsule but never arrived."""
    required = set(policy.required_kinds)
    available = {ref.kind for ref in eligible} & required
    delivered = {ref.kind for ref in kept} & required
    return sorted(available - delivered)


def check_tool(policy: RoleContextPolicy, tool: str) -> None:
    """``tool_visibility`` is an allowlist once declared; empty means unrestricted."""
    if policy.tool_visibility and tool not in policy.tool_visibility:
        raise ContractError(
            "AF-ROLE-CONTEXT-TOOL",
            f"role={policy.role}; tool={tool} not in tool_visibility; "
            "unlock=add the tool to the role's allowlist in rules/role_context.yaml",
        )


def visibility_for(policy: RoleContextPolicy, plane: str) -> VisibilityLevel:
    """Plane is ``memory``, ``knowledge`` or ``artifact``; unknown planes are hidden."""
    level = getattr(policy, f"{plane}_visibility", "none")
    return level if level in VISIBILITY_RANK else "none"


__all__ = [
    "ORIGIN_RANK",
    "VISIBILITY_RANK",
    "admit_refs",
    "check_tool",
    "default_policy",
    "filter_refs",
    "order_required_first",
    "parse_policies",
    "policy_for",
    "required_missing",
    "visibility_for",
]
