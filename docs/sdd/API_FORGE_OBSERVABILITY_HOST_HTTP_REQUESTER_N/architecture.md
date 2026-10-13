---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "13628d8269dce5393a208a6e54528dca0da7df06d06a054e17f89e65bc8ad67e"
files: [src/apiforge/observability/http_requester.py, tests/observability/test_http_requester.py]
decisions:
  - id: injected-http
    decision: injetar callback HttpGet
    rationale: testes não abrem rede e o host controla timeout, retry e headers
    rollback: retornar ao requester fake-only
  - id: endpoint-allowlist
    decision: exigir HTTPS, host explícito e sem fragmento
    rationale: reduzir SSRF e endpoints não resolvidos
    rollback: bloquear todo requester externo
---
# architecture

`HostHttpRequester` é uma barreira pequena entre o transport e a infraestrutura do host.
