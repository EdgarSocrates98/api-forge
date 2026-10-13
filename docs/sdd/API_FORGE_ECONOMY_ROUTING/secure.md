---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "6a5dae6749490026d97ab2817a853f75d85591bce25ad30537b3ce82d7d2b1eb"
threat_model: docs/security/threat-model-mvp.md
---
# secure

A requested profile can only raise the effective profile above the risk
floor, never lower it. Trims never touch reviewer/critic/referee roles; a
change there fails with `AF-ECONOMY-ROLE-INVARIANT`. An L0 stop never produces
ACCEPTED. `sdd classify` reads only local contracts and paths.
