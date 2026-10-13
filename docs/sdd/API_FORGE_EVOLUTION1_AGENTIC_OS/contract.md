---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENTIC_OS
phase: contract
profile: critical
status: ready
upstream:
  path: intent.md
  sha256: "695dad75e71a280540d9eb6c1b31c14d2eecde70e238daf713906cce2438ee09"
covers:
  - memory-contracts
  - governed-memory-store
  - blackboard-store
  - semantic-checkpoint
  - trust-taint-gate
  - cli-mcp-parity
  - deterministic-evals
  - documentation-and-evidence
---

# contract

New additive contracts are registered as v1 siblings and keep `extra=forbid`:

- `MemoryTrust`, `MemoryRecord`, `MemoryCandidate`, `MemoryPolicy`,
  `MemoryQuery`, `MemoryOutcome`, `MemoryRetrievalResult` and
  `MemoryInvalidation`;
- `BlackboardEntry`, `BlackboardQuery` and `BlackboardResult`;
- `SemanticCheckpoint`.

The application writes JSONL records under `.apiforge/memory/` and
`.apiforge/blackboard/`; invalidation and supersession are events, not deletes.
The effective-state checkpoint is JSON and is intentionally separate from the
existing economy checkpoint.

