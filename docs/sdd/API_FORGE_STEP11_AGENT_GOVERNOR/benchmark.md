---
sdd: 1
feature: API_FORGE_STEP11_AGENT_GOVERNOR
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1542 passed, 2 skipped (phase-3 wave baseline)
  recorded_at: "2026-10-06"
results:
  - focused suite: 46 passed (phase-4 scope incl. mcp surface tests)
  - evals agent-governor: 4/4 cases; deterministic pure-function path
  - all primitives are O(n) over declared signals/policy rows; no I/O
upstream:
  path: secure.md
  sha256: "02f8799d253ecf941f69a7ac8ebb686b0a0f2eabd3b5f94f89b60f8d40c26146"
---

# benchmark

No provider calls and no ledger I/O: governor decisions are pure policy math,
gain is a weighted mean over up to eight signals, recovery is a yaml lookup,
loop detection scans a bounded window. The cost story of the phase is the
spend it prevents — a STOP below threshold or a blocked loop is a measured
decision, not an assertion.
