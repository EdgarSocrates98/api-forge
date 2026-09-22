---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "f9e92f593e4d66a28cc43827576d0a41e606861b0011c0683a1bf3b2eb7fbfe9"
problem: >
  Requesters reais precisam de parâmetros específicos sem acoplar credenciais,
  rede ou SDKs ao núcleo determinístico.
success: [provider-query-encoding, credential-free-builder, backward-compatible-params]
out_of_scope: [live-http, sdk-installation, provider-mutation]
owner: api-forge-observability
---
# intent

Separar a intenção canônica da codificação de consulta de cada backend.
