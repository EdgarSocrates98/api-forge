---
sdd: 1
feature: API_FORGE_MULTILANGUAGE_MIGRATION_READINESS_B
phase: architecture
profile: migration
status: draft
upstream:
  path: contract.md
  sha256: "e259c63bd2036f3898f4079266e65477044abef0404700938fbb7c77662a3ff5"
files: [src/apiforge/migration/matrix.py, src/apiforge/migration/planner.py, src/apiforge/migration/contracts.py]
decisions:
  - id: matrix-direction
    decision: derivar direção pelos índices declarados da matriz
    rationale: upgrades e downgrades não devem ser confundidos
    rollback: remover direction do resultado
  - id: plan-gate
    decision: anexar readiness ao MigrationPlan
    rationale: o executor recebe o gate junto do DAG
    rollback: voltar a planos sem readiness
---
# architecture

O planner mantém-se read-only e agrega readiness antes de qualquer execução.
