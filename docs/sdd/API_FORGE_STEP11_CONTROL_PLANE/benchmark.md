---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1582 passed, 2 skipped (phase-4 wave baseline)
  recorded_at: "2026-10-06"
results:
  - focused suite: 14 passed (phase-5 scope incl. mcp surface tests)
  - evals control-plane: 3/3 cases; deterministic ledgers, no provider calls
  - route_status is O(rows) over a small modes overlay; shadow append is O(1)
upstream:
  path: secure.md
  sha256: "32a59c87c928b967e177e928180eeb96d72bb984a150f3749f8d90b24f082ec6"
---

# benchmark

All operations are local file math: a yaml load, an overlay scan and one
append per evaluation. The real benchmark of the phase is governance
correctness — that a candidate can never govern before its gates pass —
which the eval corpus asserts, not a latency figure.
