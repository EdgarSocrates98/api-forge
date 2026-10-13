---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: secure
profile: critical
status: draft
upstream:
  path: verify.md
  sha256: "767027f53644ad436eae6c0d1b48254ee06d28f3e2b3011d307c245468b1bf5a"
threat_model: docs/security/threat-model-mvp.md
---
# secure

Closes the review's release blocker: no case, fact or graph path can pull a file outside the project or declared workspace repositories into `ctx://`, and tampered cases are refused. Five threat-model rows added (EN and PT-BR). The CI change only selects which token enables auto-merge; the PR token stays optional and least-privilege.
