---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: plan
profile: critical
status: draft
tasks:
  - id: p0-truthfulness
    title: preserve unresolved AgentOps token usage and evidence semantics
    covers:
      - AgentOps preserves unresolved and partial token observation with explicit coverage and model-call correlation
    tests: tests/agentops/test_inspect_waste.py
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p0-truthfulness.md
  - id: p0-loop
    title: persist strategy history and enforce loop policy in the runtime
    covers:
      - loop detection observes persisted strategy history and changes execution when policy blocks a repeated strategy
    tests: tests/governance/test_loop.py and runtime supervisor integration
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p0-loop.md
  - id: p0-recovery
    title: move failure classification and recovery decision before retry
    covers:
      - recovery classifies failures and decides before any retry, with observable action and bounded attempts
    tests: tests/governance/test_recovery.py and tests/runtime/test_scheduler.py
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p0-recovery.md
  - id: p0-retrieval
    title: align retrieval ranking, sufficiency and graph contribution
    covers:
      - retrieval ranking and sufficiency use the same per-level effective score and real graph provenance
    tests: tests/knowledge/test_levels.py and retrieval eval corpus
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p0-retrieval.md
  - id: p1-routing
    title: integrate task-class-aware model router in shadow mode
    covers:
      - model routing is task-class aware and integrated in shadow mode without bypassing Decision Control Plane authority
    tests: tests/runtime/test_model_router.py and model-routing eval corpus
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p1-routing.md
  - id: p1-authority
    title: converge decision, trust and MCP target authorization
    covers:
      - tool/trust authorization is role-aware, delegation-aware and default-deny for unknown MCP targets
    tests: tests/trust/test_tools.py and MCP gateway integration
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p1-authority.md
  - id: p1-memory
    title: enforce freshness/runtime matching and explicit memory conflicts
    covers:
      - memory freshness and runtime compatibility govern eligibility and conflicts remain explicit
    tests: tests/memory/test_retrieval.py and memory eval corpus
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p1-memory.md
  - id: p1-agentops
    title: expose coverage semantics, timeline and waste evidence
    covers:
      - model-call, token, cost and trace coverage remain labeled; timeline preserves missing order evidence
    tests: tests/agentops/test_inspect_waste.py and evals agentops
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p1-agentops.md
  - id: p1-lab-mcp
    title: add executable local Lab scenarios and modern MCP proof
    covers:
      - modern MCP local proof, executable Lab scenarios and local release evidence match implementation status
    tests: tests/labs/test_scenario_proofs.py and tests/mcp
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/p1-lab-mcp.md
  - id: release-evidence
    title: produce local release receipt and update operational documentation
    covers:
      - modern MCP local proof, executable Lab scenarios and local release evidence match implementation status
    proof: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/release.md
upstream:
  path: architecture.md
  sha256: "b09749d5ac3c9643a3c1dbcdcf0b9cd53485e6ae3e9054c292281c0be6e49f51"
---

# plan

Each task is independently verified and committed. A P0 gate must pass before
the next P0/P1 wave is promoted. Every task keeps its scope bounded to the
canonical owner and includes a focused runtime proof where applicable.
