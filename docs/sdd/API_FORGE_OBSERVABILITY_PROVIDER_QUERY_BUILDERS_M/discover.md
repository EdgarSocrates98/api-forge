---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M
phase: discover
profile: standard
status: draft
approaches:
  - id: generic-only
    summary: enviar sempre os mesmos parâmetros para todos os providers
    verdict: refused -- perde semântica e dificulta requesters reais
  - id: typed-provider-encoding
    summary: codificar cada provider a partir de um ReadPlan canônico
    verdict: chosen -- separa intenção de integração
chosen: typed-provider-encoding
---
# discover

O adapter já tinha um plano canônico, mas ainda não possuía uma tradução explícita para as APIs de observabilidade.
