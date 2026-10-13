---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: discover
profile: standard
status: draft
approaches:
  - id: vendor-sdk-core
    summary: instalar e chamar SDKs de vendors no núcleo
    verdict: refused -- acoplamento, secrets e rede implícita
  - id: optional-callback-exporters
    summary: gerar payloads e enviar somente via callback do host
    verdict: chosen -- desacoplado e seguro por padrão
chosen: optional-callback-exporters
---
# discover

O control plane já produzia métricas; faltava uma saída opcional para OTel, Datadog e Dynatrace.
