---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: discover
profile: standard
status: draft
approaches:
- id: deterministic-role-layer
  summary: selector, role context planner, deltas/packet, shadow sampler and agent audit as additive deterministic
    modules
  verdict: chosen -- routing decisions unchanged, bytes measurable per role
- id: new-orchestrator
  summary: prompt compiler per role replacing invocation building
  verdict: refused -- parallel orchestrator rejected by prompt section 12
- id: llm-referee-summary
  summary: summarize positions with a model before the referee
  verdict: refused -- pays tokens to save tokens (section 9)
chosen: deterministic-role-layer
---
# discover

Source: `prompt_evo_economy.md` §26–§32, §36–§38, §84–§87. Every invocation received `spec.inputs` and the same prompt; packs were never selected from intent; debate submissions were free text; challengers were planned but never run.
