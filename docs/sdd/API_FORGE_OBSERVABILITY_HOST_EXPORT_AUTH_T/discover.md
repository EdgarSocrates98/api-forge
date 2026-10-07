---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: discover
profile: standard
status: draft
approaches:
  - id: core-secret-resolution
    summary: resolver token e montar headers no API Forge
    verdict: refused -- viola isolamento e governança
  - id: explicit-host-binding
    summary: binding aprovado delega autenticação ao host
    verdict: chosen -- auditável e sem secrets no core
chosen: explicit-host-binding
---
# discover

Os exporters geravam payloads, mas ainda faltava ligar endpoint, credencial e aprovação de forma governada.
