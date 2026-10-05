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
    observed: false
  - metric: governance overhead
    target: bounded local computation with no provider call
    observed: false
  - metric: retrieval and memory semantics
    target: provenance and configurable coverage with unresolved states
    observed: false
  - metric: lock and protocol reproducibility
    target: lock check and protocol claim match local evidence
    observed: false
upstream:
  path: secure.md
  sha256: "07f56593cd1edb555fba6d3e43ae696c6e5640d929b68449e0865f02a9a33978"
---

# benchmark

Benchmarks measure local deterministic work only. Performance claims about
providers, cloud services, production traffic or SLOs are outside the evidence
boundary and remain unresolved.
