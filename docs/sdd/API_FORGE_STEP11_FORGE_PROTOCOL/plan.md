---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [capability-matrix, task-lifecycle, risk-gate, governed-projection, evidence-bundle, peer-handoff, health-report, refusal-codes, cli-mcp-surface]
    test: sdd/API_FORGE_STEP11_FORGE_PROTOCOL/evidence/G1-focused-tests.txt
  - id: G2
    covers: [eval-corpus]
    test: sdd/API_FORGE_STEP11_FORGE_PROTOCOL/evidence/G2-evals.txt
  - id: G3
    covers: [capability-matrix, refusal-codes]
    test: sdd/API_FORGE_STEP11_FORGE_PROTOCOL/evidence/G3-gates.txt
upstream:
  path: architecture.md
  sha256: "2a3e2d153a7cf31d3bc06efa67cf938cf636df24c73dc0db220588ab09e5c159"
---

# plan

G1 — focused pytest over the protocol lifecycle + the MCP registry
expectation set. G2 — the deterministic eval corpus (4 cases). G3 —
Ruff/format/mypy-strict gates over the new surface.
