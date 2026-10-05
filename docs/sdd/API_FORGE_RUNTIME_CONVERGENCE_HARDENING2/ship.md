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
  sha256: "a0092791b601776a3cdc6668bd9fa98f9dc641954d50e88f19c1def6c25b1139"
---

# ship

Ship is permitted only after the local release receipt, full verification,
SDD check, independent task acceptance and explicit unresolved/deferred gaps
are recorded.
