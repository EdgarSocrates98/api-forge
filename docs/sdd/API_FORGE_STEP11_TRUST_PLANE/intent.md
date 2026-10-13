---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: intent
profile: critical
status: done
risk_class: high
upstream:
  path: discover.md
  sha256: "25a9896301e5c1b30e7493e5b94a10501b4d9ab481783bf32a772200466b7e1e"
problem: origin/trust/taint metadata lives only inside the memory plane;
  capsules, tool results, MCP responses, handoffs and external content carry
  no uniform trust annotation, and trust-insufficient candidates hard-reject
  instead of reaching a reviewable state
success: one TrustUnit vocabulary annotates every boundary, propagation is
  deterministic and never widens authority, tool authorization is
  allowlist-first default-deny, the §14 pipeline adds quarantine, retrieval is
  ranked and explainable, and checkpoint parity is proven by test
out_of_scope:
  - provider/model calls or semantic embeddings (optional bonus only)
  - wiring authorize() into the runtime dispatcher (later governor phase)
  - mutating v1 ContextRef/MemoryRecord/BlackboardEntry payloads
---

# intent

Deliver one trust vocabulary for every context-bearing surface, contract-
enforced:

- `TrustUnit`/`TrustedRef`/`TrustPropagation` annotate and carry trust across
  capsules, memory, blackboard, knowledge, tool results, MCP responses,
  handoffs and external content — without mutating v1 payloads;
- propagation is deterministic: taint unions, trust floors at the weakest
  source, one-tier evidence-backed lift only, authority never widens;
- `ToolRiskProfile`/`AgentPermissionSet`/`ToolAuthorization` implement §13
  allowlist-first authorization with `AF-TOOL-*` refusals;
- the §14 memory gate pipeline runs persist/quarantine/reject with an
  append-only `quarantine.jsonl` and a human review boundary;
- §15 deterministic ranked retrieval; §16 advisory invalidation triggers;
  §17 continuous-vs-resumed checkpoint parity proof.

Done when: focused tests green, registry+docs complete, catalog codes added,
existing memory/blackboard tests unchanged and green, SDD gates pass.
