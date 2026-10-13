---
sdd: 1
feature: API_FORGE_MULTILANGUAGE_MIGRATION_READINESS_B
phase: contract
profile: migration
status: draft
upstream:
  path: intent.md
  sha256: "3efb1bb224ed824327e0b9b177aa4702578f7cd0595c2bae840f7d84353ccff0"
covers: [MigrationReadiness/v1, MigrationPlan/v1]
api_ir:
  input: MigrationSpec and DiscoveryResult
  output: plan with direction, versions and readiness gate
---
# contract

Readiness distingue pronto, revisão e bloqueio; ausência de capability não é inferida como disponível.
