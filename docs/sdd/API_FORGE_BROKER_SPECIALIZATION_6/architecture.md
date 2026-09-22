---
sdd: 1
feature: API_FORGE_BROKER_SPECIALIZATION_6
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "3deb441316e763cef8530d80cc8b250944a9a94cbd142aa976300f0e28c63c17"
files: [src/apiforge/adapters/streaming.py, src/apiforge/contracts/stubs.py, src/apiforge/cli.py]
decisions:
  - id: shared-broker-adapter
    decision: manter vocabulário comum e tokens por broker
    rollback: separar scanners por protocolo
  - id: no-consume
    decision: scanners não iniciam clientes de broker
    rollback: desabilitar adapters live
---
# architecture

RabbitMQ, NATS e Pulsar entram no mesmo boundary offline de Kafka/MSK.
