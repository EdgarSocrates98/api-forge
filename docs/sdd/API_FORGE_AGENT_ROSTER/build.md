---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: build
profile: critical
status: draft
upstream:
  path: plan.md
  sha256: "6d0c633dd3f86cd1c65b38b0d3763cdb03a5859ee7ff19aa78605deb14a5b30e"
tasks:
- id: w1-infrastructure
  status: done
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/routing-baseline.json
- id: w2-roster
  status: done
  evidence: sdd/API_FORGE_AGENT_ROSTER/evidence/audit.json
claims:
- single-source-render
- render-drift-gate
- contract-lint
- referential-integrity
- deprecation-aliases
- routing-eval
- roster-25-keep
---
# build

Wave 1 (`ecbc870`): renderer, drift/reference gates, aliases (inactive), routing eval and pre-registered golden cases. Wave 2: 25 English agents, 33 absorbed files removed, aliases active, playbooks merged, rules and supervisor migrated. Critic fixes: `state-writer` access, tool existence and playbook checks in lint, real command ownership, 80-case independent holdout and 4-gram leakage metric. Report: `.claude/sdd/reports/BUILD_REPORT_API_FORGE_AGENT_ROSTER.md`.
