---
sdd: 1
feature: API_FORGE_ANALYTICAL_DATA_SPECIALIZATION_5
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "8f20a75e50d6312240a00fa6cf146591a14811bf0fe4e8aef1e864bc5d43150e"
files: [src/apiforge/adapters/analytical.py, src/apiforge/contracts/stubs.py, src/apiforge/cli.py]
decisions:
  - id: common-analytical-ir
    decision: compartilhar IR para busca e warehouse com engine explícita
    rollback: separar contratos se a semântica divergir
  - id: bounded-analysis
    decision: sinalizar busca sem paginação como risco, sem interromper scan
    rollback: classificar apenas como unresolved
---
# architecture

O adapter é textual, determinístico e sem conexões a OpenSearch ou Redshift.
