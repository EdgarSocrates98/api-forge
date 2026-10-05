---
sdd: 1
feature: API_FORGE_STEP11_AGENTOPS
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [run-inspection, inspection-sections, evidence-labeled-metrics, waste-findings, run-comparison, cli-mcp-surface]
    test: sdd/API_FORGE_STEP11_AGENTOPS/evidence/G1-focused-tests.txt
  - id: G2
    covers: [eval-corpus]
    test: sdd/API_FORGE_STEP11_AGENTOPS/evidence/G2-evals.txt
  - id: G3
    covers: [evidence-labeled-metrics]
    test: sdd/API_FORGE_STEP11_AGENTOPS/evidence/G3-gates.txt
upstream:
  path: architecture.md
  sha256: "cff3d8bb7e1fbcdc9a02d75094f0df53e8a0d34a1192d475a75de88799a8a58e"
---

# plan
