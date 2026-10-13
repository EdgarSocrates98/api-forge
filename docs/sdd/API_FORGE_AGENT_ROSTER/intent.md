---
sdd: 1
feature: API_FORGE_AGENT_ROSTER
phase: intent
profile: critical
status: draft
upstream:
  path: discover.md
  sha256: "162711478d9b6ffbe6f33ec8042fa93cbfe5535d1f89ba205cab511716d599e4"
problem: 'The 52 coordinators were mostly indistinguishable stubs in mixed languages with no permissions
  and a Codex mirror outside any gate, so agent quality depended on the host.'
success:
- single-source-render
- render-drift-gate
- contract-lint
- referential-integrity
- deprecation-aliases
- routing-eval
- roster-25-keep
out_of_scope:
- per-agent-answer-goldens
- executor-rewrite
- concrete-model-ids
- alias-removal
owner: api-forge-agents
risk_class: high
risk_signals:
- path:src/apiforge/dispatch/mirrors.py
- path:src/apiforge/runtime/supervisor.py
- path:src/apiforge/rules/playbooks.yaml
---
# intent

See `.claude/sdd/features/DESIGN_API_FORGE_AGENT_ROSTER.md`.
