# Receita — evoluir um contrato sem quebrar consumidores

**O quê:** `apiforge diff contract` classifica mudanças entre duas
versões de contrato OpenAPI como compatible, risky, breaking ou
unresolved.
**Por que:** nem toda mudança é breaking — adicionar campo opcional é
compatible, remover é breaking, e a classificação correta evita tanto
sobregovernaça quanto quebra.
**Quando:** versionamento de API, deprecação de campo/endpoint,
planejamento de v2.
**Quando não:** mudança protobuf — aí é `apiforge grpc diff` (ver
[grpc](grpc.md)).

## Problema

"Vou renomear `id` para `user_id` e adicionar `email` — o que quebra?"

## Pré-requisitos

`apiforge` instalado; contrato baseline (`v1.yaml`) e candidato
(`v2.yaml`).

## Passo a passo

```bash
apiforge diff contract --baseline api/v1.yaml --candidate api/v2.yaml
apiforge next-step    # caso o diff persista findings no case
```

## Saída esperada / interpretação

Lista de mudanças classificadas com a regra que decidiu: `compatible`
(adições opcionais), `risky` (default mudou, enum estreitou),
`breaking` (remoção, tipo, requerido novo), `unresolved` (sem evidência
para decidir — nunca chuta).

## Verificação

Cada classe carrega a regra determinística — a saída é auditable; se uma
mudança sair `unresolved`, o desbloqueio é a evidência nomeada.

## Limitações

O diff julga o documento — semântica de negócio ("o campo mudou de
significado") não é detectável por diff estrutural.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| tudo `breaking` | schema reordenado | normalize refs antes do diff |
| `unresolved` | mudança sem regra coberta | a regra que faltou é o trabalho real |

## Uso por agentes

A skill `api-forge-contract` conduz a classificação com o mesmo
vocabulário — o resultado do `diff contract` é evidência de case.
