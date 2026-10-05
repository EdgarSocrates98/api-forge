---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: plan
profile: critical
status: done
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
  - id: lab-trust-boundary
    title: close deterministic lab coverage and compact gateway authorization
    covers:
      - declared lab scenarios have replayable local proof pointers and explicit external limits
      - compact MCP gateways fail closed through an explicit risk-policy subject
    proof: sdd/API_FORGE_EVO_CONVERGENCE/evidence/lab-trust-boundary.md
upstream:
  path: architecture.md
  sha256: "ccf2af5682fd1d1e23bb5bea2c2b4578304d57d84b8d4db687db673af007f63c"
---

# plan

Work is delivered in sealed waves. Each wave has focused tests, a deterministic
receipt, a reviewable commit and a restamped SDD chain. External provider work,
deployment, merge and vulnerability-database freshness remain explicit gates.
