---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1650 passed, 2 skipped (phase-9 wave baseline)
  recorded_at: "2026-10-06"
results:
  - "focused suite: 26 passed, 1 skipped in ~4.4s"
  - "evals forge-protocol: 4/4 deterministic, each case on an isolated root"
  - "capabilities listing is O(declared descriptors); submit/attach/inspect are O(1) store ops; evidence O(attached artifacts)"
  - "token cost: zero — the boundary is deterministic, no model call anywhere in the lifecycle"
upstream:
  path: secure.md
  sha256: "969f6fde15f7b5c22d3594ff83a241b19b22ab0447788c49891c5bba2087e4eb"
---

# benchmark

The protocol adds constant-time validation + JSON persistence per verb.
The heaviest path (result projection over a governed task) reads the
TaskSpec store and brief pipeline already priced by the governed runtime.
