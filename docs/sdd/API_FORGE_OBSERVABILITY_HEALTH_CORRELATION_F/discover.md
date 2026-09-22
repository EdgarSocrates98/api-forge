---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F
phase: discover
profile: standard
status: draft
approaches:
  - id: vendor-specific
    summary: cada backend decide saúde isoladamente
    verdict: refused -- perde correlação e portabilidade
  - id: evidence-correlation
    summary: sinais, SLOs e performance em contrato comum
    verdict: chosen -- mantém decisão explicável
chosen: evidence-correlation
---
# discover

O control plane já normaliza OTel e avalia SLOs, mas faltava uma visão de saúde operacional para agents.
