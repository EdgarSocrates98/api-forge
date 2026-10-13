---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: contract
profile: critical
status: done
covers:
  - surface-audit
  - evidence-labeled-findings
  - task-disclosure
  - page-contract
  - tool-benchmark
  - compliance-matrix
  - cli-mcp-surface
  - eval-corpus
contracts:
  - ToolSurfaceAudit/v1
  - SurfaceFinding/v1
  - ToolDisclosure/v1
  - DisclosurePolicy/v1
  - ToolPage/v1
  - PageWindow/v1
  - ToolBenchmark/v1
  - ToolBenchmarkSample/v1
  - ToolBenchmarkReport/v1
refusals:
  - "AF-MCP-SURFACE-POLICY: audit thresholds file unreadable or missing"
  - "AF-MCP-DISCLOSURE-POLICY: disclosure task_classes missing"
  - "AF-MCP-BENCHMARK-POLICY: benchmark samples missing"
upstream:
  path: intent.md
  sha256: "7c905f6da7119516243a88c7f617c7092963110f35ee4e583799a646d66a5d7c"
---

# contract

Hypothesis-level findings are contractual — the `evidence` field separates
measured facts from shape suspicions.
