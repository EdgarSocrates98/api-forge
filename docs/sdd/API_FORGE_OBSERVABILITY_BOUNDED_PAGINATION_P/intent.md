---
sdd: 1
feature: API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "a868e769f69fdd82e73f409314192b564013fbdfae5b0b1f5aa3103b3c2fecfb"
problem: leituras paginadas não podem consumir recursos indefinidamente.
success: [provider-page-tokens, max-pages, cumulative-safety-budgets]
out_of_scope: [provider-mutation, unbounded-streaming, circuit-breaker]
owner: api-forge-observability
---
# intent

Normalizar tokens de página e impor limite cumulativo de páginas, registros e bytes.
