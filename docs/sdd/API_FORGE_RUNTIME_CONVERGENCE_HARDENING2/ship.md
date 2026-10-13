---
sdd: 1
feature: API_FORGE_RUNTIME_CONVERGENCE_HARDENING2
phase: ship
profile: critical
status: done
deviations:
  - provider freshness, deployment safety, production SLOs and external CI runner health remain outside local proof
evidence:
  - path: decisions/API_FORGE_HARDENING2_BASELINE.md
  - path: decisions/API_FORGE_HARDENING2_OUTCOME_BRIEF.md
  - path: sdd/API_FORGE_RUNTIME_CONVERGENCE_HARDENING2/evidence/release.md
upstream:
  path: benchmark.md
  sha256: "2a2048067caf394ac7af2fb8604326a5fb2e5585f3d96f6dd81c610ad2a7ed0e"
---

# ship

Local ship gate passes after release receipt, full verification, SDD check,
independent task acceptance and explicit unresolved/deferred gaps. External
ship remains gated by provider, deployment, security-feed and CI receipts.
