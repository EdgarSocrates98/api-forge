---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: contract
profile: critical
status: done
upstream:
  path: intent.md
  sha256: "3af658d4e35614894f6d12bdeb298b6ce3762e32c404803efa218daebf2accc9"
covers:
  - trust-contracts
  - trust-plane
  - taint-propagation
  - tool-authorization
  - memory-security-v2
  - memory-retrieval-v2
  - invalidation-triggers
  - checkpoint-parity
---

# contract

Registered contracts (all `VersionedContract`, frozen, extra-forbid):

- `TrustUnit/v1` — subject, boundary, origin, trust_level, taint,
  instruction_authority, scope, provenance, freshness, evidence_refs.
  Validator: non-`none` authority requires origin `system`/`governed_policy`.
- `TrustedRef/v1` — ContextRef + TrustUnit sidecar.
- `TrustPropagation/v1` — transform, derived unit, derived_from, taint_reduced.
- `ToolRiskProfile/v1` — tool, non-empty risk_classes, reversible, notes.
- `AgentPermissionSet/v1` — subject, allowed/denied tools, allowed risk classes.
- `ToolAuthorization/v1` — decision + AF-TOOL-* triad.
- `MemoryGateResult/v1` — verdict persist/quarantine/reject, gates passed/failed.
- `MemoryQuarantine/v1` — append-only quarantine/release row.
- `MemoryInvalidationPlan/v1` — advisory ids + rationale + unresolved.
- `MemoryScore/v1`, `MemoryRankedResult/v1` — §15 decomposition.

Widened vocabularies (additive, v1 payloads still validate): `MemoryOrigin`
gains `knowledge`; `MemoryState`/`MemoryAction` gain `quarantined`.

Refusal codes added to `docs/catalog-contract.md`: `AF-MEMORY-TRUST-QUARANTINED`,
`AF-MEMORY-EXPIRED`, `AF-MEMORY-GATE-DENIED`, `AF-MEMORY-QUARANTINE-NOT-FOUND`,
`AF-MEMORY-QUARANTINE-REJECTED`, `AF-TRUST-PROPAGATION-EMPTY`,
`AF-TOOL-PROFILE-MISSING`, `AF-TOOL-AUTHZ-DENIED`, `AF-TOOL-DENIED`,
`AF-TOOL-RISK-DENIED` (plus the legacy `AF-MEMORY-TRUST-INSUFFICIENT` marked
superseded).
