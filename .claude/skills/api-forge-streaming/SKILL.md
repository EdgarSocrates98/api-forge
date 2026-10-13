---
name: api-forge-streaming
description: >-
  Analisa streams e brokers — Kafka/MSK, Kinesis, RabbitMQ, NATS e Pulsar —
  por facts, StreamingAccessIR e dumps offline, cobrindo tópicos/streams,
  partições/shards, consumer groups, producers, acks, idempotência do
  producer, commit de offset, retry, DLQ, ordenação, rebalance e backpressure,
  sem tocar brokers. Use para revisar produtores e consumidores Kafka,
  "consumer lag", "mensagens fora de ordem", escolher chave de partição,
  auditar configuração MSK ou desenhar retry/DLQ em stream. Não use para SQS,
  SNS ou EventBridge (→ api-forge-messaging) nem para medir lag/throughput sob
  carga (→ api-forge-performance).
compatibility: >-
  Offline; requer o CLI `apiforge` e fonte ou dump versionado. Consumer lag,
  throughput e garantias de entrega exigem evidência runtime aprovada;
  `collect msk` é opt-in e read-only.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — streaming e brokers

Em streams, configuração parece garantia mas não é: `acks=all` sem
`min.insync.replicas` adequado, ou idempotência sem commit transacional,
ainda perde ou duplica. Esta skill extrai o que o código e a configuração
declaram e mantém a garantia runtime como pergunta aberta até haver medição.

## Antes de começar

Siga `api-forge-core` e rode `next-step` antes de escolher o especialista.

## Procedimento

1. **Código:**
   ```text
   apiforge model kafka-access --path <dir>
   apiforge model kinesis-access --path <dir>
   apiforge model rabbitmq-access --path <dir>
   apiforge model nats-access --path <dir>
   apiforge model pulsar-access --path <dir>
   apiforge model msk-access --path <dir>
   ```
   Contrato de eventos, se houver: `apiforge model asyncapi --path <doc>`.
2. **MSK** (postura, opt-in, read-only; antes, `apiforge evidence gate --question "..."`):
   `apiforge collect msk --cluster-arn <arn> --out <dump> --now <ISO>` e depois
   `apiforge model msk --path <dump>`.
3. **Monte o `StreamingAccessIR`**: tópicos/streams/subjects/exchanges,
   grupos, roles, operações e gaps.
4. **Verifique por camada:**
   - Producer: `acks`, idempotência, retries + `max.in.flight`, chave de
     partição (ordem só vale por chave), compressão, tamanho de mensagem.
   - Consumer: commit manual vs auto, commit antes/depois do efeito,
     rebalance e efeito duplicado, poison message, retry topic/DLQ,
     paralelismo vs ordenação.
   - Broker/stream: replicação, `min.insync.replicas`, retenção, shards
     Kinesis e limites por shard, filas duráveis/quorum (RabbitMQ),
     JetStream (NATS), subscription type (Pulsar).
5. **Julgue** com `apiforge judge --facts <facts.json>`; detalhe em
   `apiforge rules lookup <id>`.
6. **Separe estático de runtime.** Exactly-once, ordenação efetiva, lag,
   throughput, replay e backpressure nunca são inferidos da configuração.

## Guardrails

- Não publique, consuma, faça replay nem commit/reset de offset.
- Não crie nem altere tópicos, filas, subjects, subscriptions ou exchanges.
- `ack`, `retry` ou DLQ observados não provam confiabilidade; provam que a
  intenção foi declarada.
- Recomende teste de carga, chaos ou benchmark só com baseline e rollback
  (`api-forge-performance`, `apiforge perf chaos`).

## Entrega

`StreamingAccessIR`, matriz de access patterns (producer/consumer × tópico ×
chave × garantia declarada), riscos (perda, duplicata, desordem, lag),
evidências lidas, `unresolved` e o teste recomendado para o adapter runtime
aprovado.

Especialista típico: `api-event-driven-architect`.
