---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [surface-audit, task-disclosure, page-contract, tool-benchmark, cli-mcp-surface]
    test: sdd/API_FORGE_STEP11_MCP_SURFACE/evidence/G1-focused-tests.txt
  - id: G2
    covers: [eval-corpus]
    test: sdd/API_FORGE_STEP11_MCP_SURFACE/evidence/G2-evals.txt
  - id: G3
    covers: [evidence-labeled-findings, compliance-matrix]
    test: sdd/API_FORGE_STEP11_MCP_SURFACE/evidence/G3-gates.txt
upstream:
  path: architecture.md
  sha256: "f87aacca65cc538cc42ededb4405ebfbcdfd39c271ea3df64dd98cb4534f49f9"
---

# plan
