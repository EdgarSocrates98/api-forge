---
name: api-forge-messaging
description: >-
  Analisa mensageria AWS orientada a filas e eventos — SQS, SNS, EventBridge e
  orquestração com Step Functions — a partir de código, IaC e dumps offline,
  cobrindo topologia producer → destino → consumer, IAM roles, retry, DLQ,
  redrive, visibility timeout, ack/delete, FIFO/deduplicação e idempotência do
  consumidor. Use para revisar um fluxo assíncrono AWS, "mensagens estão
  sumindo/duplicando", desenhar DLQ e retry, auditar regras do EventBridge ou
  fan-out SNS→SQS. Não use para Kafka/MSK, Kinesis, RabbitMQ, NATS ou Pulsar
  (→ api-forge-streaming) nem para bancos (→ api-forge-data-access).
compatibility: >-
  Offline; requer o CLI `apiforge`. Collectors AWS são opt-in, read-only e
  produzem dumps; o core nunca lê secrets nem publica/consome mensagens.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — mensageria AWS (SQS, SNS, EventBridge)

Falhas assíncronas são silenciosas: a mensagem duplicada ou perdida só
aparece dias depois, no dado errado. Esta skill torna a topologia e as
garantias explícitas e separa o que a configuração prova do que só métricas
runtime podem provar.

## Antes de começar

Siga `api-forge-core` (caso, `next-step`). Liste filas, tópicos, buses e
regras pelo inventário de `api-forge-discovery` ou pelo IaC.

## Procedimento

1. **Código e IaC:**
   ```text
   apiforge model sqs-access --path <dir>
   apiforge model sns-access --path <dir>
   apiforge model eventbridge-access --path <dir>
   ```
2. **Postura AWS declarativa** (opt-in, credencial do host, read-only):
   ```text
   apiforge collect sqs --queue-url <url> --out <dump> --now <ISO>
   apiforge collect sns --topic-arn <arn> --out <dump> --now <ISO>
   apiforge collect eventbridge --event-bus <bus> --out <dump> --now <ISO>
   apiforge collect iam-role --role-name <role> --out <dump> --now <ISO>
   apiforge collect stepfunctions --state-machine-arn <arn> --out <dump> --now <ISO>
   apiforge model sqs|sns|eventbridge|iam-role|stepfunctions --path <dump>
   ```
   Pergunte antes com `apiforge evidence gate --question "..."`: pergunta
   estática fica no código/IaC; só pergunta de efeito runtime ganha leitura
   live read-only.
3. **Produza o `MessagingAccessIR`** e a topologia producer → destino →
   consumer, com roles que permitem cada seta.
4. **Verifique por destino:**
   - SQS: DLQ e `maxReceiveCount`, visibility timeout ≥ tempo de
     processamento × margem, long polling, delete só após sucesso, batch
     com falha parcial (`ReportBatchItemFailures`), FIFO e deduplicação.
   - SNS: filtros de assinatura, DLQ por assinatura, fan-out para SQS,
     raw delivery.
   - EventBridge: padrão da regra, alvo, retry policy e DLQ do alvo, input
     transformer, archive/replay declarado.
   - Consumidor: idempotência por chave de negócio, efeito colateral antes
     do ack, poison message.
5. **Julgue** com `apiforge judge --facts <facts.json>` e
   `apiforge rules lookup <id>`.
6. **Declare como gap** tudo que só runtime prova: backlog, idade da mensagem
   mais antiga, throughput, ordenação efetiva, exactly-once e custo.

## Guardrails

- Não publique, consuma, delete, purgue nem faça redrive/replay de mensagens.
- Não altere filas, tópicos, regras, buses, roles ou DLQs.
- Ausência de DLQ no dump não prova que não existe se a fonte for parcial;
  diga qual fonte foi lida.
- "At-least-once" é o padrão AWS: duplicata é esperada, idempotência é
  requisito, não otimização.
- Mutação AWS exige adapter do host, identidade, aprovação e rollback.

## Entrega

`MessagingAccessIR`, facts, findings com regra, diagrama textual dos fluxos
assíncronos, riscos de confiabilidade (perda, duplicata, poison, reprocesso),
evidências lidas e próximos testes verificáveis (ex. teste de idempotência,
chaos de consumidor via `apiforge perf chaos`).

Especialista típico: `api-event-driven-architect`.
