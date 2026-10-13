# Receita — medir antes de alegar economia de tokens

**O quê:** o plano `economy` mede custo por chamada — `economy report`
por verbo, `economy doctor` mostra o que faz a sessão pagar mais,
`economy stats` rola bytes por run.
**Por que:** "economizou contexto" sem medição é invenção — o API Forge
grava `payload_bytes` por chamada e só marca `provider_tokens` quando um
transcript de host os fornece.
**Quando:** decidir entre `context capsule` e o case inteiro, medir o
efeito de `detail_level`, auditar o custo de uma sessão.
**Quando não:** estimar tokens sem transcript — o sistema declara
`unresolved`, e é proposital.

## Problema

"Vale a pena usar `detail_level summary` ou `context capsule` aqui?"

## Pré-requisitos

Sessões já rodadas (o ledger acumula bytes por verbo em
`.apiforge/`); opcionalmente um transcript de host para tokens reais.

## Passo a passo

```bash
apiforge economy report                 # bytes por verbo desta run
apiforge economy doctor                 # o que faz esta setup pagar mais
apiforge economy stats                  # rollup por run e fonte
apiforge economy tier                   # menor tier que a evidência prova
```

## Saída esperada / interpretação

Bytes medidos por verbo; `detail_level_effect` quando aplicável;
`provider_tokens` só com transcript — senão `tokens_unresolved`.

## Verificação

A conta nunca mistura bytes com tokens: bytes são medidos pelo API
Forge, tokens exigem transcript — a saída separa os dois campos.

## Limitações

Sem transcript de host, nenhum número de token sai — é honestidade, não
falta de feature.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `tokens_unresolved` | nenhum transcript fornecido | exporte o transcript do host |
| report vazio | ledger sem dados ainda | rode verbos primeiro |

## Uso por agentes

`context capsule` + `economy` é o padrão de sessão longa — veja a skill
`api-forge-context` para o protocolo completo.
