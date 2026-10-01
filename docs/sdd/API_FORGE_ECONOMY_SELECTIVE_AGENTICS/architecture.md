---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "cb7c9562aab4c85351b3f4f6f14c138d42ea37a58dcedd7366fd681c977be667"
files:
- src/apiforge/contracts/selective.py
- src/apiforge/rules/expertise_triggers.yaml
- src/apiforge/rules/role_context.yaml
- src/apiforge/knowledge/selector.py
- src/apiforge/runtime/role_context.py
- src/apiforge/runtime/shadow.py
- src/apiforge/runtime/supervisor.py
- src/apiforge/debate/packet.py
- src/apiforge/agentops/agent_audit.py
- src/apiforge/evals/selective.py
decisions:
- id: one-capsule-per-run
  decision: roles take kind-filtered subsets of one capsule capped at share x context_bytes
  rollback: run with economy_enabled=False
- id: optional-request-fields
  decision: context travels in new AgentRequest fields, not input_refs
  rollback: drop the fields
- id: no-trigger-no-pack
  decision: selector never falls back to the whole catalog
  rollback: none needed
- id: observational-shadow
  decision: shadow sampled by run id hash, only from calls after the reserve, never in the result
  rollback: 'shadow_share: 0'
- id: report-only-audit
  decision: agents audit never removes or merges
  rollback: none needed
---
# architecture

contracts → selector / role_context / shadow → supervisor; debate packet depends on the debate store; agent audit reads agents/*.md and the runtime catalog.
