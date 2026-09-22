---
sdd: 1
feature: API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "4097439afa9ed90b7e15858c089233b1baf5e7c1aa0253ac39c7af436ebc2785"
tasks:
  - id: capacity-contract
    covers: [CapacityAssessment/v1]
    test: sdd/API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C/evidence/perf-tests.txt
    risk: low
    rollback: remover contrato e registro
  - id: capacity-assessment
    covers: [capacity-assessment, safe-tps-envelope]
    test: sdd/API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C/evidence/perf-tests.txt
    risk: medium
    rollback: manter apenas perf verdict
  - id: missing-evidence
    covers: [inconclusive-on-missing-evidence]
    test: sdd/API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C/evidence/perf-tests.txt
    risk: medium
    rollback: bloquear envelope quando qualquer evidência faltar
---
# plan

Implementar contrato, composição do veredito e testes de falha e ausência.
