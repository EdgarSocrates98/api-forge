---
sdd: 1
feature: API_FORGE_EVO_CONVERGENCE
phase: benchmark
profile: critical
status: draft
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
  sha256: "47e7060f1d9c4c321998b78c65ff882ee27f4b5835af28b55d85988441a14734"
---

# benchmark

Benchmarks measure local deterministic work only. Performance claims about
providers, cloud services, production traffic or SLOs are outside the evidence
boundary and remain unresolved.
