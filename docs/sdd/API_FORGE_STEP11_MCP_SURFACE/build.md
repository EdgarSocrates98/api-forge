---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: nine contracts + registry + exports + catalog codes + contract docs
    files: [src/apiforge/contracts/tool_surface.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/, docs/catalog-contract.md]
  - id: B2
    summary: audit + disclosure + benchmark modules, page helper, three rules files
    files: [src/apiforge/mcp/audit.py, src/apiforge/mcp/disclosure.py, src/apiforge/mcp/benchmark.py, src/apiforge/output/page.py, src/apiforge/rules/tool_surface.yaml, src/apiforge/rules/tool_disclosure.yaml, src/apiforge/rules/tool_benchmark.yaml]
  - id: B3
    summary: three mcp verbs + three MCP tools + docstring/limit engineering + compliance doc + eval + tests
    files: [src/apiforge/cli_tool_host.py, src/apiforge/mcp/tools.py, docs/mcp-compliance.md, src/apiforge/evals/tool_surface.py, evals/corpus/tool-surface/, tests/mcp/test_surface_v2.py, tests/mcp/test_tools.py]
claims:
  - "audit findings dropped 20 -> 0 after docstring, limit and declared-exception engineering"
  - "disclosure routes seven declared task classes with honest fallback"
  - "benchmark labels every token figure estimated"
upstream:
  path: plan.md
  sha256: "fd03ee7cb5c6631aff339a3ea52247a9e93019b61f0fceb5044d515a30eba898"
---

# build
