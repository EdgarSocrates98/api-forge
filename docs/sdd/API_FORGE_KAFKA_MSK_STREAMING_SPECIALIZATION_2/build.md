---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "5443d10dbf294752f71077d662dd137021ded53acedbfbfb1adb7d5c0fb1a88d"
tasks:
  - id: kafka-streaming
    status: done
    evidence: sdd/API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2/evidence/kafka-tests.txt
claims: [kafka-msk-ir, producer-consumer-signals, no-offset-mutation]
---
# build

Implementado `StreamingAccessIR/v1`, `model kafka-access` e `model msk-access`.
