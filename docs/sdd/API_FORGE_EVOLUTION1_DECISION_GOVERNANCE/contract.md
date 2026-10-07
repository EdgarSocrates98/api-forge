---
sdd: 1
feature: API_FORGE_EVOLUTION1_DECISION_GOVERNANCE
phase: contract
profile: critical
status: done
upstream:
  path: intent.md
  sha256: "882d3a6fe4d5f5f7f25cf1a304095d7dcdf73f13d3261ad4b973a4498409bace"
covers: [decision-contract, evidence-gate, approval-gate, cli-mcp-parity, documentation-and-evidence]
---

# contract

`DecisionRequest/v1` is never authorization. `DecisionGateResult/v1` records
the outcome and refusal metadata. Existing `AgenticPolicy/v1` and
`ApprovalGate/v1` remain the policy and human evidence inputs.
