---
sdd: 1
feature: API_FORGE_STEP11_TOKEN_ECONOMICS
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1436 passed, 2 skipped (phase-0 main baseline)
  recorded_at: "2026-10-05"
results:
  - focused suite: 50 passed, 1 skipped (phase-3 scope incl. mcp surface tests)
  - evals token-economics: 4/4 cases; deterministic pure-function path
  - aggregation/pricing/reconciliation are O(n) over already-loaded rows; no I/O growth
upstream:
  path: secure.md
  sha256: "9637cb3beee134ee96e141b89ef4c06da3e4a7c3bef444a75d08b8ca3e39421e"
---

# benchmark

No provider calls: usage rows derive from host transcripts or declared
estimates, pricing comes from declared yaml, reconciliation is pure math
over the ledger. The benchmark that matters is calibration error itself,
exercised by the corpus: observed-vs-estimate deltas are measured, never
asserted.
