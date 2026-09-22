---
sdd: 1
feature: API_FORGE_HOST_ACTIVATION_PLAN_I
phase: discover
profile: standard
status: draft
approaches:
  - id: silent-install
    summary: editar configuração do host automaticamente
    verdict: refused -- risco externo e difícil de auditar
  - id: approval-plan
    summary: gerar plano de ativação por host
    verdict: chosen -- humano decide aplicação
chosen: approval-plan
---
# discover

Paridade do core foi confirmada; ativação de hooks e runtime continua host-specific.
