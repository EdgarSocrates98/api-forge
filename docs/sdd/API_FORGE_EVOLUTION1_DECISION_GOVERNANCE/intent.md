---
sdd: 1
feature: API_FORGE_EVOLUTION1_DECISION_GOVERNANCE
phase: intent
profile: critical
status: done
risk_class: high
problem: >
  A proposed agentic action can be represented without a uniform deterministic
  result that distinguishes allow, review and block at the side-effect boundary.
success: [decision-contract, evidence-gate, approval-gate, cli-mcp-parity, documentation-and-evidence]
out_of_scope: [external-mutation, provider-calls, automatic-approval, credential-storage]
upstream:
  path: discover.md
  sha256: "1d53050c47c0a7c56432c384b45302d7331b92c1c2edd76a6136ed3093319cc6"
---

# intent

Make authorization explicit and auditable without performing the requested
action.
