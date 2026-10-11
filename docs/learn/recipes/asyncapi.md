# Receita — ler um contrato AsyncAPI em IR canônico

**O quê:** `apiforge model asyncapi` extrai um documento AsyncAPI 2.x/3.x
para o IR de mensageria.
**Por que:** contratos de eventos sofrem do mesmo drift que OpenAPI —
o IR torna canais, schemas e bindings comparáveis determinísticamente.
**Quando:** revisão de contrato de eventos, onboarding de produtor/
consumidor Kafka/SQS/EventBridge, pré-diff.
**Quando não:** provar comportamento do broker em runtime — o adapter lê
o documento, não o cluster.

## Problema

"O `asyncapi.yaml` promete esses canais e payloads — o que ele declara
de fato?"

## Pré-requisitos

`apiforge` instalado; documento AsyncAPI 2.x ou 3.x no disco.

## Passo a passo

```bash
apiforge model asyncapi --path asyncapi.yaml --detail-level full
```

## Saída esperada / interpretação

IR JSON com canais, operações, mensagens e schemas — cada campo com
proveniência no documento.

## Verificação

Campos sem declaração no documento saem `unresolved`, nunca inventados —
confira a lista `unresolved` do IR antes de citar uma capacidade.

## Limitações

Bindings de vendor (SASL, IAM) são lidos como declaração; validação de
schema dos payloads segue o que o documento declara, não o que o
produtor emite em runtime.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| versão rejeitada | documento não é 2.x/3.x | confira o campo `asyncapi:` do YAML |

## Uso por agentes

O IR alimenta `apiforge-messaging` e `apiforge-streaming` — entregue o
IR, não o YAML bruto, ao especialista.
