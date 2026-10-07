---
sdd: 1
feature: API_FORGE_MULTILANGUAGE_MIGRATION_READINESS_B
phase: plan
profile: migration
status: draft
upstream:
  path: architecture.md
  sha256: "a7858e79eeb07d04ac663b0efe9aa7e55e4d79c655f7baf6e05b24c554cc75b2"
tasks:
  - id: matrix
    covers: [runtime-direction, intermediate-versions]
    test: sdd/API_FORGE_MULTILANGUAGE_MIGRATION_READINESS_B/evidence/migration-tests.txt
    risk: medium
    rollback: remover direction do matrix resolver
  - id: readiness
    covers: [readiness-status]
    test: sdd/API_FORGE_MULTILANGUAGE_MIGRATION_READINESS_B/evidence/migration-tests.txt
    risk: high
    rollback: remover MigrationReadiness do planner
---
# plan

Adicionar direção explícita e readiness ao plano de migração.
