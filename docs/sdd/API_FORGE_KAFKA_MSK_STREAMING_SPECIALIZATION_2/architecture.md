---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "7c1db140427b5f216ec74712a71179f78c79de39722c61a9074b9d63e544bf45"
files: [src/apiforge/adapters/streaming.py, src/apiforge/contracts/stubs.py, src/apiforge/cli.py]
decisions:
  - id: shared-kafka-ir
    decision: reutilizar o mesmo IR para Kafka self-managed e Amazon MSK
    rollback: separar somente se provider facts divergirem
  - id: static-delivery-signals
    decision: registrar commit/retry/ack/transaction como sinais, não como garantia
    rollback: marcar esses sinais unresolved
---
# architecture

O collector MSK permanece responsável pela postura AWS; o scanner é independente do broker.
