---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "33633f2b42cb5c26a178945b5cd8bd568fb11c5b60d9e4be065daca7d625deba"
problem: >
  O agente não conseguia relacionar código Kafka a tópicos, grupos, roles,
  commits, retries, acks e transações sem inventar comportamento do broker.
success: [streaming-ir, kafka-msk-model, no-offset-mutation]
out_of_scope: [consumer-lag-live, topic-creation, offset-commit]
owner: api-forge-streaming
---
# intent

Adicionar análise Kafka/MSK estática e portátil para Java, Go e Python.
