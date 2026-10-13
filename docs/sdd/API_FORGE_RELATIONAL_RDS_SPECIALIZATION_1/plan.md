---
sdd: 1
feature: API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "3b27743cf7010159b7d006c04b97d3eabe2cf8c96a33616f5ed23524631c09d9"
tasks:
  - id: relational-scanner
    covers: [relational-source-ir]
    test: sdd/API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1/evidence/rds-tests.txt
    risk: medium
    rollback: remover adapters/relational.py
  - id: rds-collector
    covers: [rds-posture-dump]
    test: sdd/API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1/evidence/rds-tests.txt
    risk: medium
    rollback: remover collect_rds
  - id: offline-boundary
    covers: [no-live-query]
    test: sdd/API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1/evidence/rds-tests.txt
    risk: high
    rollback: bloquear collector sem client injetado
---
# plan

Implementar facts relacionais, collector RDS e testes com fixtures/client fake.
