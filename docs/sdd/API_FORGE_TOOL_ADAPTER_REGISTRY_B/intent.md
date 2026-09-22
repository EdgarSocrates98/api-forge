---
sdd: 1
feature: API_FORGE_TOOL_ADAPTER_REGISTRY_B
phase: intent
profile: standard
status: done
upstream:
  path: discover.md
  sha256: "cbd632c1b082e27abdf59bd421d631bf198c739500408dda6db9f49782d3f42f"
problem: >
  Agentes não tinham uma visão tipada e única das capacidades, limites,
  segurança e evidências produzidas pelas ferramentas disponíveis.
success:
  - typed-tool-adapters
  - safety-classification
  - evidence-producer-discovery
  - host-readable-cli
out_of_scope:
  - instalar ferramentas
  - executar novos binários
  - alterar allowlist sem adapter e parser
owner: api-forge-agentops
---

# intent

Expor um Tool Adapter Registry derivado do registry determinístico existente,
evitando duplicação e mantendo execução local/CI governada.
