---
name: api-forge-messaging
description: Analisa SQS, SNS, EventBridge e Kinesis como mensageria AWS, com destinos, roles, retry, DLQ, visibility, ack/delete e idempotência por evidência offline.
compatibility: Collectors AWS são opt-in e produzem dumps; não leia secrets nem execute publish/consume no core.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Carregue o caso persistido, `AGENT_PROTOCOL.md` e o próximo passo roteado.
2. Use `model sqs-access`, `model sns-access`, `model eventbridge-access` e
   `model kinesis-access` para código/configuração.
3. Use collectors somente para postura declarativa AWS e modele o dump offline.
4. Produza `MessagingAccessIR`, topologia producer→destino→consumer e sinais
   de retry, DLQ, visibility, ack/delete e idempotência.
5. Declare como gap tudo que só métricas runtime podem provar: backlog, lag,
   throughput, ordering, exactly-once e custo.

## Guardrails

- não publique, consuma, delete ou replay mensagens;
- não altere filas, tópicos, regras, streams ou DLQs;
- não trate ausência de DLQ como prova de que não existe sem fonte suficiente;
- mutação AWS exige adapter host-owned, identidade, approval e rollback.

## Entrega

Entregue IR, facts, findings, fluxos assíncronos, riscos de confiabilidade,
evidências e próximos testes verificáveis.
