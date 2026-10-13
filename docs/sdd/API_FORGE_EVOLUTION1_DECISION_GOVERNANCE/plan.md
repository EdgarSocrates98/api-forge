---
sdd: 1
feature: API_FORGE_EVOLUTION1_DECISION_GOVERNANCE
phase: plan
profile: critical
status: ready
upstream:
  path: architecture.md
  sha256: "b43f21f5088bb52103b033914c913c2120a10482bd372a4d9cf0bdee6751423a"
tasks:
  - id: D1
    covers: [decision-contract, evidence-gate]
    test: sdd/API_FORGE_EVOLUTION1_DECISION_GOVERNANCE/evidence/D1.txt
  - id: D2
    covers: [approval-gate, cli-mcp-parity]
    test: sdd/API_FORGE_EVOLUTION1_DECISION_GOVERNANCE/evidence/D2.txt
  - id: D3
    covers: [documentation-and-evidence]
    proof: sdd/API_FORGE_EVOLUTION1_DECISION_GOVERNANCE/evidence/D3.txt
---

# plan

Add contracts and pure evaluator, persist only gate results, expose CLI/MCP and
verify default-deny, evidence-required, pending/rejected/approved paths.
