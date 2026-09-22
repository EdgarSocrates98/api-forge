---
sdd: 1
feature: API_FORGE_DATA_ACCESS_GOVERNED_ADAPTERS_E
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "080b09956484639d12a186c4a5f9dc1b094402e1e0e9b0f5eeabd793520fae67"
files: [src/apiforge/data_governance.py, src/apiforge/contracts/stubs.py, src/apiforge/adapters/dbaccess.py]
decisions:
  - id: ir-boundary
    decision: governar o DataAccessIR sem executar os scanners novamente
    rollback: remover assess_data_access
  - id: explicit-mutation
    decision: reconhecer mutações por vocabulário fechado e exigir aprovação
    rollback: marcar padrões desconhecidos como review
---
# architecture

O readiness fica entre extração estática e adapters host-owned.
