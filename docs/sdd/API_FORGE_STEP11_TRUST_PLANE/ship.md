---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: ship
profile: critical
status: done
upstream:
  path: benchmark.md
  sha256: "c295f58359baab82d637b997f64104317d920dc2da51a13ff788c657ef463cc8"
deviations:
  - authorize() ships as a control-plane primitive; orchestrator wiring into
    runtime dispatch is deferred to the governor phase (phase 4)
  - AF-MEMORY-TRUST-INSUFFICIENT is superseded by AF-MEMORY-TRUST-QUARANTINED;
    the code stays in the catalog for old outcomes
evidence:
  - docs/sdd/API_FORGE_STEP11_TRUST_PLANE/evidence/G1.txt
  - docs/sdd/API_FORGE_STEP11_TRUST_PLANE/evidence/G2.txt
  - docs/sdd/API_FORGE_STEP11_TRUST_PLANE/evidence/G3.txt
rollback: revert this commit; quarantine.jsonl rows are additive-only data and
  remain valid under v1 reads (unknown action rows are simply skipped by older
  query filters, which scan records.jsonl only)
---

# ship

Phase 2 (prompt §8–§18) delivered:

- Unified trust taxonomy transversal to capsules, memory, blackboard,
  knowledge, tool results, MCP responses, handoffs and external content;
- DATA IS NOT INSTRUCTION enforced by contract validators and by the locked
  `MemoryTrust.instruction_authority="none"`;
- deterministic taint propagation with evidence-bounded lift;
- §13 tool risk profiles + allowlist-first permission sets, default deny;
- §14 memory gates persist/quarantine/reject + append-only quarantine log +
  human review boundary;
- §15 deterministic ranked retrieval, §16 advisory invalidation triggers,
  §17 checkpoint parity proof, §18 four-compactions doc distinction;
- CLI + MCP parity for the new memory verbs; catalog codes + contract docs.
