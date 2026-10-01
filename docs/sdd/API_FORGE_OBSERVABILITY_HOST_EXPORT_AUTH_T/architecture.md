---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "45608910efd9b6c8319357fdaf2e557924d35a0df5e0cb6a0b3a1b4b38e0f878"
files: [src/apiforge/contracts/observability.py, src/apiforge/observability/host_export.py, tests/observability/test_host_export.py]
decisions:
  - id: four-gates
    decision: exigir provider, credential, enabled/approval e endpoint antes do sender
    rationale: evitar envio acidental ou não autenticado
    rollback: desabilitar todo export host-owned
  - id: sender-owns-auth
    decision: callback recebe somente referência opaca
    rationale: host resolve secret, headers, timeout e retry
    rollback: voltar a payload-prepared only
---
# architecture

`execute_host_export` valida o binding e delega o envio; nenhum cliente HTTP é criado pelo core.
