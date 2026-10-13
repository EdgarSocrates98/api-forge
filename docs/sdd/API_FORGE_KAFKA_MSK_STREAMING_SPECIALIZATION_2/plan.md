---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "9104ea9b01b72c6f7aeedd25f0204de2eaad49982edb4ce92f788ff06fa4180d"
tasks:
  - id: streaming-contract
    covers: [StreamingAccessIR/v1]
    test: sdd/API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2/evidence/kafka-tests.txt
    risk: low
    rollback: remover IR
  - id: kafka-scanner
    covers: [streaming-ir]
    test: sdd/API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2/evidence/kafka-tests.txt
    risk: medium
    rollback: remover adapters/streaming.py
  - id: safe-boundary
    covers: [kafka-msk-model, no-offset-mutation]
    test: sdd/API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2/evidence/kafka-tests.txt
    risk: high
    rollback: manter somente collector MSK
---
# plan

Implementar scanner Kafka/MSK, IR e comandos de modelagem offline.
