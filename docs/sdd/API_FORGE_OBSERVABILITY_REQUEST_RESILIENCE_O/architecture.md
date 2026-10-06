---
sdd: 1
feature: API_FORGE_OBSERVABILITY_REQUEST_RESILIENCE_O
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "4bd5725d91dac77caff6a4608c671f954ae5a08e5037a7b83e2122949959264c"
files: [src/apiforge/contracts/observability.py, src/apiforge/observability/provider_transport.py, src/apiforge/observability/read_adapter.py]
decisions:
  - id: transient-only
    decision: repetir apenas ConnectionError, TimeoutError e OSError
    rationale: não mascarar erros de contrato ou autenticação
    rollback: retornar ao max_attempts=1
  - id: injected-sleep
    decision: injetar sleeper
    rationale: testes determinísticos e controle do host
    rollback: usar somente tentativa única
---
# architecture

Retry fica no provider transport, depois da validação de credencial e antes da normalização/safety policy.
