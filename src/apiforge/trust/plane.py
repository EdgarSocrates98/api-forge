"""Trust-unit annotation for every context-bearing surface (step11 §9).

A single vocabulary annotates capsule refs, external content, tool results,
MCP responses and agent handoffs. ``trust_unit()`` is the only constructor
used outside tests and it enforces DATA IS NOT INSTRUCTION before any unit
reaches a consumer.
"""

from __future__ import annotations

from apiforge.contracts.agentic_memory import Freshness, MemoryOrigin, TrustLevel
from apiforge.contracts.context import ContextCapsule, ContextRef, RefOrigin
from apiforge.contracts.trust import (
    TrustBoundary,
    TrustedRef,
    TrustUnit,
)

#: Baseline trust per origin before any evidence-backed promotion (§8).
BASE_TRUST: dict[MemoryOrigin, TrustLevel] = {
    "system": "verified",
    "governed_policy": "verified",
    "verified_evidence": "verified",
    "trusted_internal": "trusted",
    "knowledge": "trusted",
    "memory": "observed",
    "tool_result": "observed",
    "model_generated": "candidate",
    "user_data": "observed",
    "external_data": "candidate",
    "external_untrusted": "untrusted",
    "unknown": "unknown",
}

#: Taint labels an origin always carries; reductions only happen through a
#: governed_verification propagation with evidence (§10).
ORIGIN_TAINT: dict[MemoryOrigin, tuple[str, ...]] = {
    "system": (),
    "governed_policy": (),
    "verified_evidence": (),
    "trusted_internal": (),
    "knowledge": ("unverified_source",),
    "memory": ("memory_derived",),
    "tool_result": ("tool_output",),
    "model_generated": ("model_generated",),
    "user_data": ("user_supplied",),
    "external_data": ("external", "unverified_source"),
    "external_untrusted": ("external", "unverified_source", "untrusted"),
    "unknown": ("unknown_origin",),
}

#: How capsule ref origins map onto the unified origin taxonomy.
REF_ORIGIN_MAP: dict[RefOrigin, MemoryOrigin] = {
    "graph": "verified_evidence",
    "contract": "verified_evidence",
    "code": "trusted_internal",
    "knowledge": "knowledge",
    "filesystem": "trusted_internal",
}

#: Default origin/taint posture for content entering through each boundary.
_EXTERNAL_BOUNDARY_ORIGIN: dict[TrustBoundary, MemoryOrigin] = {
    "context_capsule": "trusted_internal",
    "memory": "memory",
    "blackboard": "memory",
    "knowledge": "knowledge",
    "tool_result": "tool_result",
    "mcp_response": "tool_result",
    "agent_handoff": "model_generated",
    "api_spec": "external_data",
    "external_content": "external_data",
    "log": "external_data",
    "ci_output": "external_data",
    "documentation": "external_data",
    "web": "external_untrusted",
}


def trust_unit(
    origin: MemoryOrigin,
    *,
    subject: str,
    boundary: TrustBoundary,
    scope: str = "",
    provenance: tuple[str, ...] = (),
    freshness: Freshness = "unknown",
    taint: tuple[str, ...] = (),
    trust_level: TrustLevel | None = None,
    evidence_refs: tuple[str, ...] = (),
) -> TrustUnit:
    """Annotate one context unit; never lets data carry instruction authority."""
    return TrustUnit(
        subject=subject,
        boundary=boundary,
        origin=origin,
        trust_level=trust_level or BASE_TRUST[origin],
        taint=tuple(sorted(set(ORIGIN_TAINT[origin]) | set(taint))),
        instruction_authority=(
            "system" if origin == "system" else "policy" if origin == "governed_policy" else "none"
        ),
        scope=scope,
        provenance=provenance,
        freshness=freshness,
        evidence_refs=evidence_refs,
    )


def annotate_ref(ref: ContextRef, *, boundary: TrustBoundary = "context_capsule") -> TrustedRef:
    """Attach a TrustUnit to a ContextCapsule ref without mutating the ref."""
    return TrustedRef(
        ref=ref,
        trust=trust_unit(
            REF_ORIGIN_MAP[ref.origin],
            subject=ref.uri,
            boundary=boundary,
            provenance=(ref.provenance,),
            # a pinned revision is a stable snapshot; worktree content can drift
            freshness="fresh" if ref.revision != "worktree" else "unknown",
        ),
    )


def annotate_capsule(
    capsule: ContextCapsule, *, boundary: TrustBoundary = "context_capsule"
) -> tuple[TrustedRef, ...]:
    """Annotate every ref in a capsule; unresolved refs keep their own taint."""
    return tuple(annotate_ref(ref, boundary=boundary) for ref in capsule.refs)


def external_unit(
    boundary: TrustBoundary,
    *,
    subject: str,
    scope: str = "",
    provenance: tuple[str, ...] = (),
    taint: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
) -> TrustUnit:
    """Annotate content entering through an external boundary (API specs, logs,
    CI output, docs, web, MCP responses, handoffs)."""
    return trust_unit(
        _EXTERNAL_BOUNDARY_ORIGIN[boundary],
        subject=subject,
        boundary=boundary,
        scope=scope,
        provenance=provenance,
        taint=taint,
        evidence_refs=evidence_refs,
    )


__all__ = [
    "BASE_TRUST",
    "ORIGIN_TAINT",
    "REF_ORIGIN_MAP",
    "annotate_capsule",
    "annotate_ref",
    "external_unit",
    "trust_unit",
]
