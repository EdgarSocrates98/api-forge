---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: discover
profile: critical
status: done
approaches:
  - id: rewrite-tool-registry
    summary: collapse the 140-tool registry into per-domain servers
    verdict: refused -- breaks existing host configurations and the
      additive tool-name contract; audit+disclosure gets the same economy
  - id: model-based-routing
    summary: embed a model call to pick tools per task
    verdict: refused -- the control plane is deterministic; a model is not
      needed when a declared keyword policy routes honestly
  - id: audit-plus-disclosure
    summary: measure the surface, route tasks through a declared
      task-class policy, bound outputs with the §42 page contract, and
      document spec compliance in a versioned matrix
    verdict: chosen -- additive, deterministic, honest about what the
      signature cannot prove
chosen: audit-plus-disclosure
---

# discover

§40–§45 asks for tool-surface engineering v2 plus an MCP 2026 compliance
matrix. The FastMCP server, gateway and measured surface already exist;
what is missing is the audit, the declared disclosure router, the bounded
output contract, the benchmark and the compliance document.
