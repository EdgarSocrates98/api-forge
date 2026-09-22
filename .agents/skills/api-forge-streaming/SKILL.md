---
name: api-forge-streaming
description: Analisa Kafka/MSK/Kinesis, RabbitMQ, NATS e Pulsar por facts, IRs e dumps offline, cobrindo tópicos, grupos, producers, consumers, ack, retry, DLQ, ordering e backpressure sem tocar brokers.
compatibility: Requer fonte ou dump versionado; consumer lag, throughput e garantias de entrega precisam de evidência runtime aprovada.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Carregue o caso e execute `next-step` antes de escolher o especialista.
2. Use `model kafka-access`, `model msk-access`, `model kinesis-access`,
   `model rabbitmq-access`, `model nats-access` ou `model pulsar-access`.
3. Para MSK, use `collect msk` apenas para dump de postura e depois modele o
   dump offline.
4. Produza `StreamingAccessIR`, facts de tópicos/grupos/roles/operações e gaps.
5. Separe sinal estático de garantia runtime: exactly-once, ordering, lag,
   throughput, replay e backpressure nunca são inferidos.

## Guardrails

- não publique, consuma, faça replay ou commit de offset;
- não crie tópicos, filas, subjects, subscriptions ou exchanges;
- não trate `ack`, `retry` ou `DLQ` observado como prova de confiabilidade;
- recomende teste de carga, chaos ou benchmark somente com baseline e rollback.

## Entrega

Entregue IR, access-pattern matrix, riscos, evidências, unresolved e teste
recomendado para o adapter runtime aprovado.
