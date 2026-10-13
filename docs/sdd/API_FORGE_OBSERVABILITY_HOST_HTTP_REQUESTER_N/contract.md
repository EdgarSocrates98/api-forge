---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "6c7977cec68647d222334742ddc8dfb19a03ed9db2709e8207e20dc996d2f2b8"
covers: [HostHttpRequester/v1]
api_ir:
  input: resolved HTTPS endpoint, params and opaque credential reference
  output: provider mapping from host callback
---
# contract

O requester não conhece valores secretos; apenas repassa a referência opaca ao callback do host.
