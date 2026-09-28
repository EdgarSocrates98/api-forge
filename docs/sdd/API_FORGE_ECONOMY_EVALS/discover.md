---
sdd: 1
feature: API_FORGE_ECONOMY_EVALS
phase: discover
profile: standard
status: draft
approaches:
- id: deterministic-matrix
  summary: canonical contract tasks x profiles with deterministic verdicts and separate axes
  verdict: chosen -- offline, reproducible, grounded in the diff engines
- id: llm-judged-quality
  summary: judge answers with a model
  verdict: refused -- needs providers and invents quality (section 16)
chosen: deterministic-matrix
---
# discover

Source: `prompt_evo_economy.md` §34–§35 and §72–§80. Each wave had its own eval; nothing compared the profiles on the same tasks with correctness as an axis, gated future changes, replayed stored runs or measured extra agents.
