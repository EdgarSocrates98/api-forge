---
sdd: 1
feature: API_FORGE_AGENTIC_QUALITY_HOST_PARITY_G
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "9d67cdfaa9614f68a2ab4e5273afc615fcea5909a259588deae421bb500d0538"
tasks:
  - id: quality-contract
    covers: [AgenticQualityAssessment/v1]
    test: sdd/API_FORGE_AGENTIC_QUALITY_HOST_PARITY_G/evidence/quality-tests.txt
    risk: low
    rollback: remover contrato
  - id: quality-aggregation
    covers: [quality-aggregate, holdout-required, host-gaps-visible]
    test: sdd/API_FORGE_AGENTIC_QUALITY_HOST_PARITY_G/evidence/quality-tests.txt
    risk: medium
    rollback: conservar evals e parity existentes
---
# plan

Implementar agregação conservadora e testes de todos os estados.
