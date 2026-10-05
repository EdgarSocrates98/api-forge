---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: benchmark
profile: critical
status: done
baseline:
  command: uv run apiforge economy report --case .apiforge/case
  state: collected
  note: baseline is measured from the existing case and local test harness; no fabricated TPS or cost is permitted
results:
  - metric: context and AgentOps projection correctness
    target: canonical names, separate dimensions, deterministic correlation
    observed: true
    result: focused tests and full suite passed
  - metric: governance overhead
    target: bounded local computation with no provider call
    observed: true
    result: governor, loop/recovery and tool authorization tests passed
  - metric: retrieval and memory semantics
    target: provenance and configurable coverage with unresolved states
    observed: true
    result: retrieval eval passed; graph absence and cost rate remain explicit unresolved fields
  - metric: lock and protocol reproducibility
    target: lock check and protocol claim match local evidence
    observed: true
    result: uv lock check, lock audit, MCP protocol probe and SBOM generation passed
upstream:
  path: secure.md
  sha256: "c2fad4d038877ec45028ae55ae9e62e5cd22f19e45f9f1428f23fed269cb5ea6"
---

# benchmark

Benchmarks measure local deterministic work only. Performance claims about
providers, cloud services, production traffic or SLOs are outside the evidence
boundary and remain unresolved.
