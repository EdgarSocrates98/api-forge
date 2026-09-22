---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "d38c07ad7f94fbbf23e4fb07ba79602ba36cd402137e9535306beb3b610f2a2c"
problem: o runtime precisa integrar HTTP real sem controlar sockets ou segredos.
success: [https-only, explicit-host-allowlist, host-owned-credentials]
out_of_scope: [automatic-network, credential-resolution, provider-sdk]
owner: api-forge-observability
---
# intent

Delegar o GET ao host depois de validar um endpoint HTTPS explicitamente permitido.
