---
sdd: 1
feature: API_FORGE_CONTRACT_INTELLIGENCE_DIGITAL_TWIN_D
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "24b4a33ecb1e03fa4949f4ab63687409a80d57526026f19ef590638a66e62b74"
problem: >
  Contratos OpenAPI e gRPC têm diagnósticos separados e agents não conseguem
  ensaiar falhas sem subir serviços ou tocar infraestrutura.
success:
  - unified-contract-impact
  - offline-digital-twin
  - deterministic-fault-scenarios
  - no-network-proof
out_of_scope:
  - provisionar AWS
  - iniciar servidores reais
  - benchmark de latência real
owner: api-forge-contract-intelligence
---

# intent

Provide a single contract-impact result for OpenAPI and gRPC and an offline Digital Twin plan with deterministic fault scenarios. Network access and external mutation are prohibited.
