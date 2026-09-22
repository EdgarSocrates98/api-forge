---
sdd: 1
feature: API_FORGE_OBSERVABILITY_OPERATIONAL_READINESS_D
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "f34045bd70b12ca4bf42694c25e3f7719b016561178388bcb8897e55abdf6438"
files: [src/apiforge/observability/readiness.py, src/apiforge/contracts/observability.py, src/apiforge/observability/host_export.py]
decisions:
  - id: reuse-export-gates
    decision: espelhar as mesmas invariantes do envio autenticado
    rollback: remover preflight e conservar execute_host_export
  - id: provider-neutral
    decision: usar o mesmo contrato para OTel, Datadog e Dynatrace
    rollback: dividir contratos somente se os adapters divergirem materialmente
---
# architecture

O preflight é uma camada anterior ao callback do host e não possui cliente HTTP.
