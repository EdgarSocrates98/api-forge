---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "5e79104cc68bbe0498cde59d9bd8845e28105c813e4d3777b384d0918b5b493f"
problem: métricas precisam ser exportáveis sem tornar vendors obrigatórios ou ativar rede implicitamente.
success: [otel-payload, datadog-payload, dynatrace-payload, disabled-by-default]
out_of_scope: [sdk-installation, credential-resolution, automatic-export]
owner: api-forge-observability
---
# intent

Produzir payloads específicos e receipts de exportação com callback opcional.
