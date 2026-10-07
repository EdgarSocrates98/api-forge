---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "9e5e0e472c08fa6b98e2943b4693e96d19b4924647ac02b5cf3e6e78d8d64a34"
tasks:
  - id: correlator
    status: done
    evidence: sdd/API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F/evidence/health-tests.txt
claims: [incident-is-critical, missing-telemetry-is-inconclusive]
---
# build

Implementado `HealthAssessment`, `assess_health` e `observability health`.
