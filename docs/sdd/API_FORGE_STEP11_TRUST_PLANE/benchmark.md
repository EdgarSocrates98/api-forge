---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: benchmark
profile: critical
status: done
upstream:
  path: secure.md
  sha256: "a986f506b0b432d2e0fe1e55563a4bab27c138ef94fee8ad5327dcba9a5db736"
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1436 passed, 2 skipped (phase-0 main baseline)
  recorded_at: "2026-10-05"
results:
  - focused suite: 47 passed (phase-2 scope)
  - ranking adds one sort pass over already-filtered rows; no I/O growth
  - parity test proves resumed state byte-equal to continuous state
---

# benchmark

No new performance surface: annotation, propagation, authorization, gating
and ranking are pure functions over already-loaded rows. The §17 parity test
is the benchmark that matters here — a resumed run reproduces the continuous
run's decisions, facts, unresolved items, tool path and result bit-for-bit.

Full-suite delta recorded in ship.md after the wave gate run.
