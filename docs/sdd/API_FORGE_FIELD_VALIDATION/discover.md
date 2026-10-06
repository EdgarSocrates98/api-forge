---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: discover
profile: critical
status: draft
approaches:
- id: harness-only
  summary: field-run schema, record/annotate/verify/report/export joined from existing run artifacts
  verdict: recommended by the agent -- evidence before building
- id: protocol-only
  summary: markdown template and manual annotation, no code
  verdict: refused -- no verifiable gate, metrics lost, no eval export
- id: harness-plus-inference
  summary: harness plus opt-in static cross-repo relation inference, isolated from baseline runs and compared by A/B
  verdict: chosen by the owner -- isolation guardrail makes the comparison causal
chosen: harness-plus-inference
---
# discover

Source: `prompt_evo_new_forge.md` (feature-driven to evidence-driven). Critic review (`api-adversarial-critic`) rejected the raw proposal as a vision without gate: self-evaluation bias, weak n, pre-written conclusion, unverified spec versions. Brainstorm: `.claude/sdd/features/BRAINSTORM_API_FORGE_FIELD_VALIDATION.md`.
