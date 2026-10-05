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
  sha256: "4b875ccefc810aca8b458c2d025954f17c1ad2686d29ebf04db84b235dd1dc30"
---

# ship

Ship is permitted only after the local release receipt, full verification,
SDD check, independent task acceptance and explicit unresolved/deferred gaps
are recorded.
