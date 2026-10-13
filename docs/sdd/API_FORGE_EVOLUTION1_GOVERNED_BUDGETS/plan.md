---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: plan
profile: critical
status: ready
upstream:
  path: architecture.md
  sha256: "8bddfef7614c84f01220c5c6a30eb739da117262270aeab95aa9f397fe54f359"
tasks:
  - id: G1
    covers: [hierarchical-budget-contracts, append-only-admission, token-unknown-refusal]
    test: sdd/API_FORGE_EVOLUTION1_GOVERNED_BUDGETS/evidence/G1.txt
  - id: G2
    covers: [cli-mcp-budget-parity]
    test: sdd/API_FORGE_EVOLUTION1_GOVERNED_BUDGETS/evidence/G2.txt
  - id: G3
    covers: [documentation-and-evidence]
    proof: sdd/API_FORGE_EVOLUTION1_GOVERNED_BUDGETS/evidence/G3.txt
---

# plan

Implement contracts and the pure governor first, then expose identical CLI
and MCP projections, then validate refusal, accumulation, hierarchy, token
unknown and duplicate-spend behavior. No external system is in scope.
