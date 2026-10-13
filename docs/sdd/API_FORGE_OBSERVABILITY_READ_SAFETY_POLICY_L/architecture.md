---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "b607f0bcacc7bde1c8068651bd9e9ee6afb002ab3cc11e3143849f889946bf92"
files: [src/apiforge/contracts/observability.py, src/apiforge/observability/read_safety.py, src/apiforge/observability/provider_transport.py, src/apiforge/observability/read_adapter.py]
decisions:
  - id: policy-at-provider-boundary
    decision: avaliar resposta normalizada no transport antes do adapter
    rationale: evita entregar dados acima do orçamento ao core
    rollback: remover a avaliação do transport e manter fixture-only
  - id: blocked-after-network
    decision: marcar blocked com network_called=true
    rationale: diferencia falha de segurança de ausência de chamada
    rollback: bloquear qualquer receipt executado
---
# architecture

O transporte normaliza, mede e rejeita; o adapter converte a violação em receipt verificável.
