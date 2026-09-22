---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: discover
profile: standard
status: draft
approaches:
  - id: retry-only
    summary: continuar tentando durante indisponibilidade
    verdict: refused -- pode propagar saturação ao provider
  - id: provider-circuit
    summary: abrir após falhas e testar recuperação por half_open
    verdict: chosen -- falha rápida e recuperação controlada
chosen: provider-circuit
---
# discover

Retry bounded reduz falhas transitórias, mas faltava impedir novas chamadas durante indisponibilidade sustentada.
