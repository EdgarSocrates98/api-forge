---
sdd: 1
feature: API_FORGE_SECURITY_RESILIENCE_GATE_F
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "e08db1b30df79b886242f98c05f15df5ae713dece4772711eacfd0bf36a842a9"
files: [src/apiforge/safety.py, src/apiforge/contracts/stubs.py, src/apiforge/verification/service.py]
decisions:
  - id: closed-control-vocabulary
    decision: manter nove controles mínimos em vocabulário versionado
    rollback: remover a avaliação consolidada
  - id: no-inference
    decision: não inferir controle por ausência de falha
    rollback: retornar review quando a integração não declarar controles
---
# architecture

O gate compõe sinais declarados; scanners e verificadores continuam sendo as fontes de evidência detalhada.
