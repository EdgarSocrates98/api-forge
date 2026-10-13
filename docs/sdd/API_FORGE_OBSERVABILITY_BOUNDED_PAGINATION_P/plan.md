---
sdd: 1
feature: API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "923b8f0dd184e25075a714ab409b700ec5dd00ff30bcff5d9552c0edaaed441c"
tasks:
  - id: tokens
    covers: [provider-page-tokens]
    test: sdd/API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P/evidence/pagination-tests.txt
    risk: medium
    rollback: remover _next_page
  - id: budget
    covers: [max-pages, cumulative-safety-budgets]
    test: sdd/API_FORGE_OBSERVABILITY_BOUNDED_PAGINATION_P/evidence/pagination-tests.txt
    risk: high
    rollback: bloquear toda paginação externa
---
# plan

Adicionar extração de tokens, loop bounded e evidência de páginas executadas.
