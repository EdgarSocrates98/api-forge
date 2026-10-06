---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: intent
profile: critical
status: done
risk_class: high
problem: >
  API Forge has profile and phase budgets but no one deterministic admission
  decision over task, phase, role and tool spend with unresolved token state.
success:
  - hierarchical-budget-contracts
  - append-only-admission
  - cli-mcp-budget-parity
  - token-unknown-refusal
  - documentation-and-evidence
out_of_scope:
  - provider billing or model SDKs
  - automatic budget increase or silent downgrade
  - cloud, database, GitHub or production mutation
upstream:
  path: discover.md
  sha256: "eda97a6e10b81a353950a8bd1a4e61cb817ebf25b228eef4207e52f3f67a9486"
---

# intent

Deliver hierarchical budget admission with explicit `allow`, `stop` and
`unresolved` outcomes. The governor must never silently downgrade, infer token
usage or append a spend that exceeded a declared limit.

Out of scope: provider billing, model routing, cloud mutation and changing the
existing runtime supervisor semantics.
