---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: benchmark
profile: critical
status: done
baseline:
  - controlled-basetemp full pytest run
  - static MCP surface and benchmark
  - retrieval and AgentOps eval reports
results:
  - state: pass
    measure: full_pytest
    value: 1751 passed, 2 skipped
  - state: pass
    measure: mcp_benchmark_samples
    value: 10
  - state: pass
    measure: mcp_surface_tools
    value: 152
  - state: pass
    measure: lab_catalog_cells
    value: 21/21
  - state: unresolved
    measure: provider_cost_latency_slo
    note: no provider receipt; no production percentage inferred
upstream:
  path: secure.md
  sha256: "210d4311d31f41b3868551a17ee945612be96ea93cfa6521e5569492318da8a1"
---

# benchmark

The benchmark records observed test, retrieval, AgentOps, model/tool call,
runtime and MCP-surface measures. No performance or token-savings percentage
is claimed without provider-observed evidence.
