---
sdd: 1
feature: API_FORGE_GRAPH_DOCUMENT_SPECIALIZATION_7
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "2c5aeb333d74e9ea64936b4c0aacded969141739f47f996983895f88fb2fb4c4"
files: [src/apiforge/data_governance.py, src/apiforge/adapters/dbaccess.py, src/apiforge/contracts/stubs.py]
decisions:
  - id: reuse-profile
    decision: estender DataPerformanceProfile com sinais específicos
    rollback: remover riscos Mongo/Neptune
  - id: boundedness-first
    decision: tratar unbounded como risco explícito e verificável
    rollback: reportar apenas fato bruto
---
# architecture

O perfil é composto sobre as flags já produzidas pelos scanners de banco.
