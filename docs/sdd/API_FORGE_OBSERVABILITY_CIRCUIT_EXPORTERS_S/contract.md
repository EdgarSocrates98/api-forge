---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "69a3e2b8ea8959d6ad9778090f7ec6d7984429a28bc5c4cd9e9235dfe73cab6a"
covers: [CircuitMetricsExportReceipt/v1, build_export_payload/v1]
api_ir:
  input: CircuitBreakerMetrics and backend selection
  output: deterministic payload or disabled/sent/failed receipt
---
# contract

Exportadores não recebem secrets; callbacks são a única fronteira que pode executar envio.
