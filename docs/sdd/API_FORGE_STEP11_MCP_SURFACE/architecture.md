---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/tool_surface.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - src/apiforge/mcp/audit.py
  - src/apiforge/mcp/disclosure.py
  - src/apiforge/mcp/benchmark.py
  - src/apiforge/output/page.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/cli_tool_host.py
  - src/apiforge/rules/tool_surface.yaml
  - src/apiforge/rules/tool_disclosure.yaml
  - src/apiforge/rules/tool_benchmark.yaml
  - docs/mcp-compliance.md
  - evals/corpus/tool-surface/
  - tests/mcp/test_surface_v2.py
decisions:
  - "audit thresholds are declared data — the detector never hardcodes numbers"
  - "disclosure is advisory and falls back honestly; hosts decide what to load"
  - "output bounding lands via limit params, not a breaking response reshape"
  - "benchmark runs read-only samples on an isolated root, tokens labeled estimated"
upstream:
  path: contract.md
  sha256: "7c4a86e8ff8c580146b2d33296de3bdb1c6e466b4df4adefbdabdd63563d1977"
---

# architecture
