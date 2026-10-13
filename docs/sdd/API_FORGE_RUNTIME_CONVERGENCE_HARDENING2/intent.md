---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: intent
profile: critical
status: draft
problem: existing deterministic primitives are not consistently authoritative in the runtime path, and several metrics/receipts collapse unresolved state or use stale scoring inputs
success:
  - loop detection observes persisted strategy history and changes execution when policy blocks a repeated strategy
  - recovery classifies failures and decides before any retry, with observable action and bounded attempts
  - AgentOps preserves unresolved and partial token observation with explicit coverage and model-call correlation
  - retrieval ranking and sufficiency use the same per-level effective score and real graph provenance
  - model routing is task-class aware and integrated in shadow mode without bypassing Decision Control Plane authority
  - tool/trust authorization is role-aware, delegation-aware and default-deny for unknown MCP targets
  - memory freshness and runtime compatibility govern eligibility and conflicts remain explicit
  - modern MCP local proof, executable Lab scenarios and local release evidence match implementation status
out_of_scope:
  - live model/provider calls, production traffic, cloud/database/broker mutation, deploy, merge or external PR mutation
  - creation of a second runtime, Forge Kernel extraction or a new agent roster
  - active model promotion without independent evidence and explicit policy approval
upstream:
  path: discover.md
  sha256: "f4defc6a2b5cedbded3518289c3ffbe60c96efd17f5092d13698a269ec95df2d"
risk_class: low
risk_signals: [path:src/apiforge/runtime, path:src/apiforge/governance, path:src/apiforge/agentops, path:src/apiforge/knowledge, path:src/apiforge/context, path:src/apiforge/memory, path:src/apiforge/mcp, path:src/apiforge/trust, path:docs, path:tests]
---

# intent

The work is delivered in gated waves. P0 truthfulness, loop, recovery and
retrieval defects block promotion of later integrations. External limits stay
explicit as `DEFERRED_EXTERNAL` or `UNRESOLVED`.

