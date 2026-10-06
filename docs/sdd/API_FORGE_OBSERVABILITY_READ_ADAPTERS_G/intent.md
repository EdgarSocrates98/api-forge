---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_ADAPTERS_G
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "0334199af3cacdb7db6644986f69bd06e2bc399c12cb958765957cf779556a31"
problem: >
  A plataforma precisa preparar consultas multi-vendor sem permitir que uma
  ausência de credencial seja confundida com ausência de falha.
success: [provider-read-plan, fixture-proof, mutation-block]
out_of_scope: [live-network-call, credential-resolution, alert-mutation]
owner: api-forge-observability
---
# intent

Separar planejamento de consulta da execução provider-specific.
