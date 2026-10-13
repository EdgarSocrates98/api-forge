---
sdd: 1
feature: API_FORGE_BROKER_SPECIALIZATION_6
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "0979c4f0061e6345e6838b1aef25452c1f6f53e491c21901ee30b69b67c789af"
tasks:
  - id: broker-model
    covers: [StreamingAccessIR/v1, broker-ir]
    test: sdd/API_FORGE_BROKER_SPECIALIZATION_6/evidence/broker-tests.txt
    risk: low
    rollback: reverter enum de brokers
  - id: broker-scanners
    covers: [portable-streaming-model, no-consume]
    test: sdd/API_FORGE_BROKER_SPECIALIZATION_6/evidence/broker-tests.txt
    risk: medium
    rollback: remover comandos novos
---
# plan

Adicionar tokens, extractors, comandos e testes dos três brokers.
