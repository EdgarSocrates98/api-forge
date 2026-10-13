---
sdd: 1
feature: API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "8da84d5d983eff5f0b705fed21895130a18ecf8b6fcf2d3529c2e4fd373113c9"
files: [src/apiforge/contracts/observability.py, src/apiforge/observability/provider_transport.py, src/apiforge/observability/read_adapter.py]
decisions:
  - id: provider-token-normalization
    decision: extrair tokens Datadog, Dynatrace, CloudWatch e OTel para um loop comum
    rationale: manter o adapter provider-neutral
    rollback: aceitar apenas uma página
  - id: cumulative-budget
    decision: avaliar safety após cada página acumulada
    rationale: falhar cedo antes de crescer memória
    rollback: bloquear paginação
---
# architecture

Paginação vive no transport, antes do receipt e depois do retry por página.
