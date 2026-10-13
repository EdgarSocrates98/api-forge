---
sdd: 1
feature: API_FORGE_BROKER_SPECIALIZATION_6
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "c63c5405d747836e9a07df6013869c85217b61e521173b51ecd698e958f85c59"
tasks:
  - id: brokers
    status: done
    evidence: sdd/API_FORGE_BROKER_SPECIALIZATION_6/evidence/broker-tests.txt
claims: [rabbitmq, nats, pulsar, offline]
---
# build

Implementados `model rabbitmq-access`, `model nats-access` e `model pulsar-access`.
