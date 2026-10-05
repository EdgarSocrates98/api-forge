---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: ship
profile: critical
status: draft
deviations:
  - provider freshness, deployment safety, production SLOs and external CI runner health remain outside local proof
evidence:
  - path: decisions/API_FORGE_HARDENING2_BASELINE.md
upstream:
  path: benchmark.md
  sha256: "700fce1e0b2e434f633e0a0ea370961b916e9577c2b49562c6f0a10bb085f4dd"
---

# ship

Ship is permitted only after the local release receipt, full verification,
SDD check, independent task acceptance and explicit unresolved/deferred gaps
are recorded.
