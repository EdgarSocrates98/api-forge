---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: plan
profile: critical
status: draft
tasks:
  - id: p0-agentops
    title: correct AgentOps metric semantics and gate aggregation
    covers:
      - AgentOps emits canonical Context Quality metric names and tri-state decision-gate counts
      - model-call, provider-attempt, token-entry and latency metrics remain separate and correlation-bound
    proof: sdd/API_FORGE_EVO_CONVERGENCE/evidence/p0-agentops.md
  - id: convergence-governance
    title: integrate run governance and authoritative decision context
    covers:
      - execute_run records a run governance context and uses conservative governance decisions before additional work
    proof: sdd/API_FORGE_EVO_CONVERGENCE/evidence/runtime-governance.md
  - id: retrieval-memory
    title: make retrieval provenance and memory query semantics explicit
    covers:
      - retrieval and memory evals prove their declared semantics without inventing semantic/provider evidence
    proof: sdd/API_FORGE_EVO_CONVERGENCE/evidence/retrieval-memory.md
  - id: protocol-supply-chain
    title: align MCP freshness, lock evidence and production documentation
    covers:
      - MCP, CI, supply-chain and documentation claims match the locally observed implementation and current official protocol research
    proof: sdd/API_FORGE_EVO_CONVERGENCE/evidence/protocol-supply-chain.md
upstream:
  path: architecture.md
  sha256: "3ecfd26fe5e5fd0a416a7b582348130dff1fb9473424c6b7355f57948d0de37d"
---

# plan

Work is delivered in sealed waves. Each wave has focused tests, a deterministic
receipt, a reviewable commit and a restamped SDD chain. External provider work,
deployment, merge and vulnerability-database freshness remain explicit gates.
