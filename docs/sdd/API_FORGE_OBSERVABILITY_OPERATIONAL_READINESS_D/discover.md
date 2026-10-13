---
sdd: 1
feature: API_FORGE_OBSERVABILITY_OPERATIONAL_READINESS_D
phase: discover
profile: standard
status: draft
approaches:
  - id: probe-provider
    summary: testar Datadog ou Dynatrace durante o planejamento
    verdict: refused -- cria efeitos externos e depende de segredo real
  - id: offline-preflight
    summary: avaliar binding, credencial, aprovação e allowlist sem rede
    verdict: chosen -- seguro, explicável e portátil entre hosts
chosen: offline-preflight
---
# discover

Os exporters já têm gates de segurança, mas faltava diagnóstico antecipado de prontidão operacional.
