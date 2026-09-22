---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "2854633bb3f5dc78e1378f844f7a1c7639f946e879fd42a2aea38a6e1f0ba256"
problem: exportações reais precisam de autenticação e aprovação sem expor credenciais ao core.
success: [explicit-approval, credential-gate, endpoint-allowlist, send-evidence]
out_of_scope: [secret-resolution, automatic-approval, provider-sdk]
owner: api-forge-observability
---
# intent

Criar binding explícito de host para exportação autenticada e somente leitura operacional.
