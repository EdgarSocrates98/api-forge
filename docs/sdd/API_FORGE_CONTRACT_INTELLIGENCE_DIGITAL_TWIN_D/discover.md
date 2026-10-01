---
sdd: 1
feature: API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D
phase: discover
profile: standard
status: draft
approaches:
  - id: live-provider
    summary: chamar APIs e infraestrutura real durante análise
    verdict: refused -- não é seguro nem reproduzível sem amostras e credenciais
  - id: offline-twin
    summary: plano e simulação determinística sem rede
    verdict: chosen -- preserva evidências e funciona no CI
chosen: offline-twin
---

# discover

Existing OpenAPI and gRPC compatibility engines classify protocol-specific deltas, but agents lack one impact envelope and a safe way to rehearse API behavior without a server or infrastructure.
