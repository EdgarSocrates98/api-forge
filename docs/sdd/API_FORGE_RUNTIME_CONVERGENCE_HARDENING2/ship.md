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
  sha256: "caf87b2e8caf812977cbf1c02a754c252624e3b7468ff06b407ec91a7cb0e449"
---

# ship

Ship is permitted only after the local release receipt, full verification,
SDD check, independent task acceptance and explicit unresolved/deferred gaps
are recorded.
