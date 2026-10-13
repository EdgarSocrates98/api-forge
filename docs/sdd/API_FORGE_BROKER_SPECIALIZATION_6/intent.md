---
sdd: 1
feature: API_FORGE_BROKER_SPECIALIZATION_6
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "f2e852b8ec9ee501ed3dca33ed32096652d8927a4cc585b8a4dd1e83ef35b28d"
problem: >
  APIs que usam RabbitMQ, NATS ou Pulsar ficavam sem análise de producer,
  consumer, subject/queue/topic e confiabilidade.
success: [broker-ir, portable-streaming-model, no-consume]
out_of_scope: [broker-login, message-consume, topology-mutation]
owner: api-forge-streaming
---
# intent

Estender a especialização de streaming para RabbitMQ, NATS e Pulsar.
