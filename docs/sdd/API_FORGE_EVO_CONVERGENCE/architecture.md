---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: architecture
profile: critical
status: draft
files:
  - src/apiforge/agentops/inspect.py
  - src/apiforge/contracts/runtime_governance.py
  - src/apiforge/runtime/supervisor.py
  - src/apiforge/runtime/model_router.py
  - src/apiforge/knowledge/retrieval.py
  - src/apiforge/memory/retrieval.py
  - src/apiforge/mcp/server.py
  - .github/workflows/ci.yml
  - docs
decisions:
  - id: additive-projections
    decision: keep legacy reads while exposing canonical metric and receipt fields
    rollback: remove the new projection fields and retain the prior read-only view
  - id: governance-before-expansion
    decision: evaluate run governance before debate, escalation or additional work
    rollback: disable the adapter through the feature policy while preserving the receipt
  - id: local-evidence-boundary
    decision: report provider freshness, vulnerability databases and production SLOs as unresolved
    rollback: revert only the claim and receipt changes; no external mutation is required
upstream:
  path: contract.md
  sha256: "ca92ac6faffc7e3334dac0f0a7a41d1e05553dbbdee49bf4533da4877bb93254"
---

# architecture

The implementation follows the existing deterministic layers. Contracts and
receipts are the durable boundary; runtime integrations are small adapters that
can be disabled without changing the core evaluator. The execution path records
governance before optional work and keeps model calls, provider attempts, token
entries and run latency as separate axes.
