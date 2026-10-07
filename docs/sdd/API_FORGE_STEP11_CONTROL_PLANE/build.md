---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: six contracts + registry + exports + contract docs
    files: [src/apiforge/contracts/agentic_governance.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/]
  - id: B2
    summary: control_plane engine + declared routes + overlay ledgers
    files: [src/apiforge/governance/control_plane.py, src/apiforge/rules/control_plane.yaml]
  - id: B3
    summary: control CLI app, MCP read tools, eval corpus, AF codes, tests
    files: [src/apiforge/cli_control.py, src/apiforge/cli.py, src/apiforge/mcp/tools.py, src/apiforge/evals/control_plane.py, evals/corpus/control-plane/, tests/, docs/catalog-contract.md]
claims:
  - "in shadow the candidate never governs: governing=legacy and a
    ShadowRecord with sorted difference is appended atomically"
  - "promotion to active requires all five §31 requirements plus an approved
    ApprovalGate matching evidence.approval_id"
  - "every active route declares a fallback_route or is terminal; degraded
    terminal routes refuse AF-GOV-FALLBACK-MISSING"
  - demotion never requires a gate — the safe direction is always open
  - the fail-closed decision gate in governance/decision.py is untouched
upstream:
  path: plan.md
  sha256: "0d2b4024fb6e352c6be8409037fe2e4db9ebd33d6c16a6f870c34f37b0ee0efa"
---

# build
