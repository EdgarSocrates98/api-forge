---
sdd: 1
feature: API_FORGE_OBSERVABILITY_AUTHENTICATED_READ_ADAPTERS_K
phase: discover
profile: standard
status: draft
approaches:
  - id: sdk-core
    summary: importar SDKs vendors no núcleo
    verdict: refused -- acoplamento, secrets e rede
  - id: injected-transport
    summary: adapter recebe broker status e transporte externo
    verdict: chosen -- fronteira testável
chosen: injected-transport
---
# discover

O broker gate existia; faltava uma execução read-only testável para providers.
