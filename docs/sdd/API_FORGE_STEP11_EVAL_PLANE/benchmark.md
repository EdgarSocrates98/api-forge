---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: benchmark
profile: critical
status: done
baseline:
  name: full-suite
  command: pytest -q --basetemp=<host-temp>
  result: 1671 passed, 2 skipped (phase-10 wave baseline)
  recorded_at: "2026-10-06"
results:
  - "focused suite: 14 passed in ~47s (memory-gate seeding dominates)"
  - "evals trace-grading: 5/5 deterministic, O(spans x dimensions)"
  - "evals security-adversarial: 9/9 deterministic, isolated roots per case"
  - "evals memory-evals: 9/9 deterministic, real persistence per case"
  - "evals frontier: O(profiles^2) pareto over 3 profiles, instant"
  - "token cost: zero — the entire plane is deterministic and offline; the provider tier is declared, never executed"
upstream:
  path: secure.md
  sha256: "0aedc233230bdda479f3548c3c8e7fa6a1e7389cfe47598e850619db28035bb2"
---

# benchmark

No model call exists anywhere in the plane, so the marginal cost of the
new eval wave is local CPU and disk only. The slowest surface is memory
evals because seeds flow through the real persistence gates — that is
the intended cost of testing the gate, not overhead to trim.
