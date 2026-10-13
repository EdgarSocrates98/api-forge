---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "39605544b00a90be5abe1e1b5a1e87e331f4de7873285b221ead8d5735b84906"
tasks:
  - id: contract
    change: adicionar política e violações ao receipt
    covers: [bounded-records, bounded-bytes]
    test: sdd/API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L/evidence/safety-tests.txt
    risk: medium
    rollback: remover ReadSafetyPolicy e violations
  - id: boundary
    change: avaliar registros e bytes no provider transport
    covers: [explicit-blocked-receipt]
    test: sdd/API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L/evidence/safety-tests.txt
    risk: high
    rollback: bloquear todos os receipts executados
  - id: gates
    change: manter ruff, mypy e release gate
    covers: [bounded-records]
    test: sdd/API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L/evidence/safety-tests.txt
    risk: low
    rollback: não publicar sem gates
---
# plan

Implementar a barreira no boundary do provider e validar o caminho de bloqueio.
