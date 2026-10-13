# Receita — invocar um coordenador de agente do API Forge

**O quê:** os 25 coordenadores de `agents/*.md` — um por ângulo de
investigação (contrato, descoberta, mensageria, performance, segurança,
SDD…), cada um com contrato de nove seções, `access` e ferramentas
próprias.
**Por que:** o roteamento por agente é o mecanismo que coloca o
especialista certo no finding certo — escolher por nome é proibido; o
roteador decide por evidência (`apiforge next-step`).
**Quando:** caso com findings e a fase pede um especialista.
**Quando não:** nenhum finding ainda — `api-forge-discovery` primeiro;
nenhum case — `apiforge analyze` primeiro.

## Problema

"O case tem findings de contrato — quem assume?"

## Pré-requisitos

Install `--profile full` (agents só aterrissam no perfil completo);
case persistido com findings.

## Passo a passo

```bash
apiforge next-step            # o roteador nomeia o agente por evidência
apiforge agents sync          # re-render mirrors (.claude/.agents/.codex)
apiforge agents check         # drift dos mirrors — gate de release
```

No host, nomeie o perfil: "use o `api-contract-architect` como
subagente para revisar este contrato".

## Saída esperada / interpretação

`next-step` retorna o agente recomendado + a regra de roteamento que o
escolheu. `agents check` lista divergências dos mirrors — `sync`
regenera do canônico.

## Verificação

`agents lint` + `agents audit` validam o contrato de nove seções e o
anti-teatro (capacidade/papel únicos) — o release roda esses gates.

## Limitações

Mirrors são gerados — nunca edite `.claude/agents/*.md` à mão; o
canônico é `agents/*.md`. Executores (`af-*` em `agents/executors/`) são
despachados pelo coordenador, não invocados direto.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| agente "não aparece" no host | profile `recommended` (só skills) | `install --profile full` |
| drift no `agents check` | mirror editado | `apiforge agents sync` |

## Uso por agentes

O coordenador despachado não despacha subagentes — a decomposição roda
inline. `next-step` é a única fonte de rota; julgamento próprio sobre
rota é violação do AGENT_PROTOCOL.
