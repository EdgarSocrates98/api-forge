---
sdd: 1
feature: API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "3c13f925dbdc3c4a78fde54d01f192c3674708b0c711e32f1cbf12fb44eed109"
covers: [ReadSafetyPolicy.max_pages/v1, page_count]
api_ir:
  input: provider response with optional pagination token
  output: bounded accumulated records or blocked receipt
---
# contract

`max_pages` integra o orçamento de leitura; a evidência registra `page_count` quando a leitura executa.
