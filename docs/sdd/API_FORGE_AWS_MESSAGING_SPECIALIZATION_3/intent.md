---
sdd: 1
feature: API_FORGE_AWS_MESSAGING_SPECIALIZATION_3
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "92d7a3a7ba62b8207abf455611d76beca0fd98a4f2175f030a70ab9b59788be7"
problem: >
  APIs event-driven não tinham uma visão unificada de producer, consumer,
  retry, DLQ, ack/delete e idempotência.
success: [messaging-ir, reliability-signals, no-message-mutation]
out_of_scope: [publish-live, replay-live, queue-admin]
owner: api-forge-messaging
---
# intent

Criar especialização de mensageria AWS para orientar design e testes.
