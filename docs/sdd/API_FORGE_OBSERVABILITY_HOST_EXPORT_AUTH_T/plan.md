---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "bbff175e5e42b87f96081da96716ae4f313af156a3bc4b5c807990594c12a7e4"
tasks:
  - id: binding
    covers: [explicit-approval, credential-gate, endpoint-allowlist]
    test: sdd/API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T/evidence/host-export-tests.txt
    risk: high
    rollback: remover host_export.py
  - id: receipts
    covers: [send-evidence]
    test: sdd/API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T/evidence/host-export-tests.txt
    risk: medium
    rollback: bloquear todos os exports
---
# plan

Adicionar contrato de binding, gate de credencial/aprovação e sender autenticado injetável.
