---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_ADAPTERS_G
phase: discover
profile: standard
status: draft
approaches:
  - id: live-first
    summary: chamar vendors diretamente no núcleo
    verdict: refused -- mistura credenciais, rede e decisão agentica
  - id: read-plan
    summary: contrato de consulta read-only e fixture proof
    verdict: chosen -- adapters futuros ficam isolados
chosen: read-plan
---
# discover

Os adapters Datadog/Dynatrace eram apenas projeções; faltava uma fronteira explícita para consultas read-only e CloudWatch/OTel.
