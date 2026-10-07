---
sdd: 1
feature: API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "c833604d29e6d75bc4af624136c2292f503afe26c681bb7045a59d398eb522b8"
results:
  - gate: pytest tests/perf/test_capacity.py
    outcome: pass
    evidence: 4 passed
  - gate: ruff and mypy
    outcome: pending
    evidence: evidence/perf-tests.txt
---
# verify

O gate deve distinguir aprovação, falha de SLO e evidência insuficiente.
