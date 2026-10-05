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
  sha256: "9895b11c06ca3c9b148694eb24bafe1b523926b2ac51202c2f811553323eda7b"
---

# ship

Ship is permitted only after the local release receipt, full verification,
SDD check, independent task acceptance and explicit unresolved/deferred gaps
are recorded.
