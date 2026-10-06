---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: discover
profile: standard
status: draft
approaches:
- id: projection-layer
  summary: output modes, gateway MCP, slicers and a host table as projections of the unchanged core
  verdict: chosen -- measurable and lossless
- id: trim-full-surface
  summary: register fewer MCP tools per profile
  verdict: refused -- hides capability (section 89) and hosts may defer schemas anyway (section 39)
- id: llm-log-summaries
  summary: summarize logs with a model
  verdict: refused -- pays tokens to save tokens (section 9)
chosen: projection-layer
---
# discover

Source: `prompt_evo_economy.md` §39–§44 and §88–§93. Every CLI payload was pretty-printed, the MCP server published 86 tools with unmeasured cost, logs reached agents raw and nothing adapted to the host.
