---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "c1458a59f19dd46e98136ed82c386a47c15f31d809f355ddf9c62e0c8dd3fd0d"
tasks:
  - id: health-contract
    covers: [health-assessment, explicit-observability-gaps]
    test: sdd/API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F/evidence/health-tests.txt
    risk: low
    rollback: remove health.py
  - id: health-cli
    covers: [incident-correlation]
    test: sdd/API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F/evidence/health-tests.txt
    risk: medium
    rollback: remove observability health command
---
# plan

Adicionar avaliação de saúde e superfície CLI read-only.
