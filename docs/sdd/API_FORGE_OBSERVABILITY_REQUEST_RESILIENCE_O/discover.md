---
sdd: 1
feature: API_FORGE_OBSERVABILITY_REQUEST_RESILIENCE_O
phase: discover
profile: standard
status: draft
approaches:
  - id: infinite-retry
    summary: repetir indefinidamente até obter resposta
    verdict: refused -- pode travar agentes e ampliar custo
  - id: bounded-backoff
    summary: tentativas limitadas e backoff com teto
    verdict: chosen -- previsível e auditável
chosen: bounded-backoff
---
# discover

O requester host-owned precisava de resiliência explícita sem transformar falhas externas em loops infinitos.
