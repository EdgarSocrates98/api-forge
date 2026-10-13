---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "64cf4a8e661ae4e36a14569c109548a576b32ad3673e4579b5df6271e541d271"
tasks:
  - id: builders
    covers: [provider-query-encoding, credential-free-builder]
    test: sdd/API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M/evidence/query-tests.txt
    risk: medium
    rollback: remover query.py
  - id: adapter-integration
    covers: [backward-compatible-params]
    test: sdd/API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M/evidence/query-tests.txt
    risk: medium
    rollback: restaurar parâmetros genéricos no adapter
---
# plan

Adicionar builders puros, integrar no adapter e provar os quatro formatos provider-specific.
