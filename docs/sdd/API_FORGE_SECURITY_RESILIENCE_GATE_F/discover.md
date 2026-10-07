---
sdd: 1
feature: API_FORGE_SECURITY_RESILIENCE_GATE_F
phase: discover
profile: standard
status: draft
approaches:
  - id: implicit-best-practice
    summary: considerar segurança coberta por documentação
    verdict: refused -- não é verificável
  - id: explicit-control-gate
    summary: avaliar controles de segurança e resiliência declarados
    verdict: chosen -- bloqueia falhas e nomeia lacunas
chosen: explicit-control-gate
---
# discover

O projeto possui verificadores especializados, mas faltava uma visão única dos controles mínimos de uma API.
