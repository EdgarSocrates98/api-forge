---
sdd: 1
feature: API_FORGE_AWS_MESSAGING_SPECIALIZATION_3
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "813e6a95afb84c127c48c69485f8e48b57ed053a8b943cd1603cbb3d7af51dfa"
files: [src/apiforge/adapters/messaging.py, src/apiforge/contracts/stubs.py, src/apiforge/cli.py]
decisions:
  - id: unified-messaging-ir
    decision: manter SQS, SNS, EventBridge e Kinesis em uma IR fechada
    rollback: separar adapters se os sinais não forem comparáveis
  - id: reliability-is-signal
    decision: retry, DLQ, ack e idempotência são sinais, não prova de garantia
    rollback: marcar garantia como unresolved
---
# architecture

A camada de código complementa collectors AWS e permanece offline.
