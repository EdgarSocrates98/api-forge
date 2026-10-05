---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: intent
profile: critical
status: draft
problem: existing governance, evidence and economy primitives are not consistently authoritative in the runtime and AgentOps projections contain known semantic mismatches
success:
  - AgentOps emits canonical Context Quality metric names and tri-state decision-gate counts
  - model-call, provider-attempt, token-entry and latency metrics remain separate and correlation-bound
  - execute_run records a run governance context and uses conservative governance decisions before additional work
  - retrieval and memory evals prove their declared semantics without inventing semantic/provider evidence
  - MCP, CI, supply-chain and documentation claims match the locally observed implementation and current official protocol research
out_of_scope:
  - live model/provider calls, cloud mutation, production traffic, deploy, merge authorization or credential acquisition
  - extracting a shared Forge Kernel before a second compatible consumer exists
  - replacing the runtime with a single God Object
upstream:
  path: discover.md
  sha256: "167c67895e54924c374ce1df27dad4e4fe00e5142a5b795a076e3c65f563ecfe"
risk_class: high
risk_signals: [path:src/apiforge/runtime, path:src/apiforge/governance, path:src/apiforge/knowledge, path:src/apiforge/memory, path:src/apiforge/agentops, path:src/apiforge/mcp, path:.github/workflows/ci.yml, path:docs]
---

# intent

This is a large, incremental convergence wave. The acceptance status of each
sub-wave remains evidence-based; unresolved external dependencies are reported
explicitly rather than promoted to green.
