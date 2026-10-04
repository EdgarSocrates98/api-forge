---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENTIC_OS
phase: intent
profile: critical
status: draft
upstream:
  path: discover.md
  sha256: "885a6c6c34e74a2749774bcc91b583ee9c0d08317dce7f806d691c73c92a450b"
problem: >
  API Forge has durable task, context, evidence and economy artifacts but no
  single governed memory/blackboard contract that lets long-running roles
  share only scoped, provenance-bound state and resume without transcript
  reconstruction.
success:
  - memory-contracts
  - governed-memory-store
  - blackboard-store
  - semantic-checkpoint
  - trust-taint-gate
  - cli-mcp-parity
  - deterministic-evals
  - documentation-and-evidence
out_of_scope:
  - live model calls or provider SDKs
  - vector databases or semantic retrieval as a default
  - automatic promotion of model output to institutional memory
  - cloud/database/messaging mutation
  - PR creation, push, merge or deployment
risk_class: low
risk_signals: [path:src/apiforge/contracts, path:src/apiforge/runtime, path:src/apiforge/mcp, path:docs]
---

# intent

Make agentic state a first-class, deterministic and resumable part of API
Forge while preserving the existing case, context, task, evidence and
economy contracts. A memory item is data, never instruction; a blackboard item
is an append-only claim/evidence record, never a transcript; and a checkpoint
is a semantic state snapshot, never a compacted chat log.

## Acceptance intent

- Every persisted record carries scope, origin, trust/taint, provenance and
  evidence references.
- Institutional and semantic memory cannot be persisted from model-generated
  content without verified evidence.
- Retrieval filters by scope and environment and reports stale, invalidated,
  contradictory or unverifiable records instead of hiding them.
- Blackboard writes are append-only and queries return a bounded relevant
  subset.
- A checkpoint can be serialized, loaded in a fresh process and compared for
  effective-state equivalence.
- CLI and MCP expose the same canonical payloads and preserve refusal codes.

