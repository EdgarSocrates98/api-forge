---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "b327ff455fad79fa014f4c42a9fbe8d2e49841aa60e5c912f5d73a0b36adaf72"
problem: providers indisponíveis não devem consumir tentativas e rede indefinidamente.
success: [closed-open-half-open, recovery-window, circuit-evidence]
out_of_scope: [distributed-breaker, persistent-state, provider-mutation]
owner: api-forge-observability
---
# intent

Adicionar circuit breaker por transport com estados explícitos e evidência no receipt.
