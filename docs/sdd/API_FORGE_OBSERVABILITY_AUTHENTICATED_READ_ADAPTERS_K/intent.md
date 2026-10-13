---
sdd: 1
feature: API_FORGE_OBSERVABILITY_AUTHENTICATED_READ_ADAPTERS_K
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "b7cab5ea60b572b2126ea0f1b0bdf8be2443da096fa63b69fe7bf0ff19d32346"
problem: >
  Adapters reais precisam de transporte e credenciais sem contaminar o core
  determinístico ou permitir mutação.
success: [transport-injection, authenticated-read, mutation-proof]
out_of_scope: [provider-sdk-in-core, dashboard-write, alert-write]
owner: api-forge-observability
---
# intent

Executar leitura autenticada somente via dependências explícitas.
