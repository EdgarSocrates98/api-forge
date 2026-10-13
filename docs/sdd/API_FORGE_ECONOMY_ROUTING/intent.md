---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "31077295a608d872e39809cfd394a8998b596b5625ad790304857171ae943b56"
problem: >
  The router and supervisor size execution by risk alone; nothing bounds cost
  by preference, reserves verification, stops on proof or matches SDD process
  weight to change risk.
success: [economy-profiles, risk-floor-invariant, supervisor-envelope, stop-and-ladder, risk-adaptive-sdd, economy-routing-eval]
out_of_scope: [shared-cache, incremental-graph, lazy-expertise, capsule-bound-budgets, compact-mcp, quality-floor-ranking]
owner: api-forge-economy
risk_class: medium
risk_signals: [path:src/apiforge/runtime/supervisor.py, path:src/apiforge/runtime/economy.py, path:src/apiforge/contracts/routing.py, path:src/apiforge/sdd/checks.py]
---
# intent

Choose the cheapest execution that still satisfies the risk floor, and say so
explicitly when the budget or ceiling leaves the answer unresolved.
