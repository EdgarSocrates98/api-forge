---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "2b950a243b238529f733e94eb980ac83dde0420a59d3cfd36d527795c9a44e91"
files: [src/apiforge/observability/query.py, src/apiforge/observability/read_adapter.py]
decisions:
  - id: pure-query-layer
    decision: manter a codificação em função pura
    rationale: permite testes sem rede e reuso por requesters
    rollback: voltar ao conjunto de parâmetros genéricos
  - id: compatibility-keys
    decision: preservar service e environment junto às chaves específicas
    rationale: não quebrar transports existentes
    rollback: versionar o transporte e remover as chaves legadas
---
# architecture

O adapter chama o builder; o requester continua sendo uma dependência do host.
