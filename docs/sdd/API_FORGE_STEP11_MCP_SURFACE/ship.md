---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: ship
profile: critical
status: done
deviations:
  - "streamable HTTP transport stays NOT_IMPLEMENTED — stdio is the declared local transport"
  - "resources/prompts primitives stay NOT_IMPLEMENTED — tools + ctx:// refs cover reads"
  - "the §42 page contract is adopted incrementally via limit params, not a breaking reshape"
evidence:
  - docs/sdd/API_FORGE_STEP11_MCP_SURFACE/evidence/G1-focused-tests.txt
  - docs/sdd/API_FORGE_STEP11_MCP_SURFACE/evidence/G2-evals.txt
  - docs/sdd/API_FORGE_STEP11_MCP_SURFACE/evidence/G3-gates.txt
rollback: "revert this commit; new modules and params are additive — limit
  params are optional kwargs and older clients never call the new verbs"
upstream:
  path: benchmark.md
  sha256: "f8157c80c826e142fa942ee68877c584d86222699528d7d23f18530fb915d365"
---

# ship

Phase 9 delivered: measured surface audit, declared task disclosure,
bounded output contract, tool cost benchmark, three policy refusals and
the spec-2025-11-25 compliance matrix.
