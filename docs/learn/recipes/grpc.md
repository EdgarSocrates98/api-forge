# Receita — revisar e fazer diff de contrato gRPC

**O quê:** o plano de controle gRPC offline: `grpc discover` expõe o
contrato, `grpc analyze` constrói o IR canônico e `grpc diff` classifica
a evolução protobuf por regras determinísticas.
**Por que:** mudança de field number/tag é breaking silencioso — só
regra determinística pega todos os casos.
**Quando:** revisão de `.proto`, evolução de API gRPC, pré-merge de
mudança protobuf.
**Quando não:** invocar toolchains externos (`protoc`, `buf`) — o plano
é offline por design; quem compila é o CI.

## Problema

"Mudou um `.proto` — isso quebra consumidores?"

## Pré-requisitos

`apiforge` instalado; `.proto` ou descriptor no disco; baseline anterior
para o diff.

## Passo a passo

```bash
apiforge grpc discover --source service.proto
apiforge grpc analyze service.proto
apiforge grpc diff service-v1.proto service-v2.proto
```

## Saída esperada / interpretação

`discover` expõe o contrato; `analyze` emite o gRPC-IR (services, RPCs,
messages, fields com tags); `diff` classifica cada mudança —
compatible/risky/breaking — com a regra que decidiu.

## Verificação

A classificação carrega a regra — se um campo mudou de tag e o diff diz
`breaking`, a evidência é a própria regra citada, não opinião.

## Limitações

Sem runtime: o diff julga o contrato, não o comportamento do servidor.
Opções custom e plugins são declaração no IR.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `breaking` inesperado | tag reutilizada ou tipo mudou | leia a regra citada no resultado |

## Uso por agentes

O `api-contract-architect` consome o IR; o resultado do `grpc diff` é
evidência de case — anexe, não reinterprete.
