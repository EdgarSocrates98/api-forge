---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "5caf12eca88eedc1d8f11b84fd1f9c6f896298dbe22a1b86ddeca919cdfb127b"
files: [src/apiforge/contracts/observability.py, src/apiforge/observability/exporters.py, tests/observability/test_exporters.py]
decisions:
  - id: payload-builders
    decision: separar builders de payload do envio
    rationale: testes locais e integração vendor independente
    rollback: manter somente métricas internas
  - id: explicit-sender
    decision: sender opcional e disabled por padrão
    rationale: impedir mutação/rede implícita
    rollback: remover todos os senders
---
# architecture

O módulo gera formatos OTel, Datadog e Dynatrace e delega autenticação/rede ao host.
