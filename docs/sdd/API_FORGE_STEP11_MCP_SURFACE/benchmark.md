---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1634 passed, 2 skipped (phase-8 wave baseline)
  recorded_at: "2026-10-06"
results:
  - "focused suite: 19 passed, 1 skipped in ~5s"
  - "evals tool-surface: 4/4 deterministic"
  - "mcp benchmark: 10 declared samples measured, ranked by median bytes"
  - "audit is O(tools x schema); disclosure O(classes x keywords); benchmark O(samples x repeats)"
upstream:
  path: secure.md
  sha256: "4e34d1d75c1504e5b0a2bddf062de8bec7e1f46dda56e9a44a48fee99948a7df"
---

# benchmark

On-demand measurement verbs; the benchmark creates and deletes an isolated
root per run and stores nothing.
