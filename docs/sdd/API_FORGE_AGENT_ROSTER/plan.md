---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: plan
profile: critical
status: draft
upstream:
  path: architecture.md
  sha256: "fcfd02284da4f52889d3ab47ea62a3fcaf38677d59b418a1be605a98fcbca7ad"
tasks:
- id: w1-infrastructure
  covers:
  - single-source-render
  - render-drift-gate
  - contract-lint
  - referential-integrity
  - deprecation-aliases
  - routing-eval
  test: sdd/API_FORGE_AGENT_ROSTER/evidence/routing-baseline.json
  risk: medium
  rollback: revert wave 1 commit ecbc870
- id: w2-roster
  covers:
  - roster-25-keep
  test: sdd/API_FORGE_AGENT_ROSTER/evidence/audit.json
  risk: high
  rollback: revert wave 2 commit; aliases inactive restores old names
---
# plan

Wave 1 infrastructure and baseline, then wave 2 content and migration; full suite once before ship.
