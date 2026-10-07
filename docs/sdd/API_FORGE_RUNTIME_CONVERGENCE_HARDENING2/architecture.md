---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: architecture
profile: critical
status: draft
files:
  - src/apiforge/governance/loop.py
  - src/apiforge/governance/recovery.py
  - src/apiforge/runtime/scheduler.py
  - src/apiforge/runtime/supervisor.py
  - src/apiforge/agentops/inspect.py
  - src/apiforge/knowledge/levels.py
  - src/apiforge/runtime/model_router.py
  - src/apiforge/trust/tools.py
  - src/apiforge/mcp/gateway.py
  - src/apiforge/memory/retrieval.py
  - src/apiforge/labs/catalog.py
  - docs
decisions:
  - id: preserve-runtime-composition
    decision: extend supervisor and scheduler through small governed adapters; do not create a second runtime
    rollback: disable the new enforcement adapter while retaining receipts and legacy-compatible reads
  - id: evidence-first-p0
    decision: fix truthfulness, loop, recovery and retrieval before structural integrations
    rollback: revert the affected phase commit; no external state is mutated
  - id: shadow-before-authority
    decision: keep model routing and challenger observations in shadow until Decision Control Plane evidence allows promotion
    rollback: return to legacy selection and retain shadow observations as non-authoritative
  - id: local-only-proof
    decision: use deterministic fixtures and recorded local receipts for Lab/MCP; leave live-provider and production claims unresolved
    rollback: remove the projection, never widen the claim
upstream:
  path: contract.md
  sha256: "15cd9c16d2b3acece2f2d7e10a4be3d436b8fee920ddc22052615b429a9f5457"
---

# architecture

The target circuit is composed over existing owners:

`TaskSpec -> input/trust/context admission -> governance -> routing -> tool
authority -> supervisor/scheduler -> evidence/economy/OTel -> AgentOps/evals ->
gain/stop/recovery -> Decision Control Plane -> checkpoint/handoff`.

Strategy history is persisted through the existing run trajectory/store. The
scheduler executes a recovery decision rather than inventing retry policy.
Retrieval candidates carry explicit score provenance. MCP retains inner domain
gates after the gateway target authorization gate.

