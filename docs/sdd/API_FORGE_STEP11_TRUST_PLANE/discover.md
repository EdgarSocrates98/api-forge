---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: discover
profile: critical
status: done
approaches:
  - id: trust-fields-everywhere
    summary: add origin/trust_level/taint columns onto ContextRef, MemoryRecord
      and BlackboardEntry v1 contracts
    verdict: refused -- mutating frozen v1 contracts breaks backward
      compatibility; trust must travel beside the unit, not inside it
  - id: memory-only-hardening
    summary: keep the gates inside memory/store.py as inline ifs
    verdict: refused -- leaves capsules, tool results, MCP responses and
      handoffs unannotated; the mission asks for a transversal plane
  - id: trust-plane
    summary: TrustUnit contract + annotation functions per boundary,
      deterministic propagation, gate pipeline extracted to memory/security,
      allowlist-first tool authorization from yaml data
    verdict: chosen -- additive, contract-enforced, honest about authority
chosen: trust-plane
---

# discover

`prompt_evo_step11.md` phase 2 asks for a Trust Plane: unified origin/trust
taxonomy, DATA IS NOT INSTRUCTION enforcement, taint propagation, Agentic
Security v2 (tool risk + permission sets), and memory security v2
(persist/quarantine/reject, ranked retrieval, invalidation triggers,
checkpoint parity).

The repository already ships `MemoryOrigin`/`TrustLevel`/`MemoryTrust` with
`taint` and `instruction_authority="none"` locked on memory rows, an
append-only memory store with evidence gates, blackboard taint reporting and
`SemanticCheckpoint` with an `equivalent()` comparator. This wave makes that
vocabulary transversal instead of bolting on a parallel mechanism.
