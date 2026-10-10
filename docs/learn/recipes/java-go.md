# Receita — inventariar uma API Java ou Go sem contrato mantido

**O quê:** a skill `api-forge-discovery` mapeia estaticamente o que uma
API expõe — linguagem, framework, rotas, handlers, schemas, auth,
dependências, bancos, filas, IaC, testes e telemetria — e constrói o
API-IR com proveniência.
**Por que:** sem OpenAPI mantido, o contrato real é o código — descoberta
determinística sem executar nada.
**Quando:** repo Spring Boot/Java ou Go desconhecido, inventário de
rotas, migração ou revisão sem contrato de origem.
**Quando não:** o contrato OpenAPI já existe e é mantido — então
`apiforge analyze --contract` é o caminho direto (ver
[analyze-contract](analyze-contract.md)).

## Problema

"Não há `openapi.yaml` — como o agente inventaria as rotas? Ele não
inventa: descobre no código."

## Pré-requisitos

`apiforge` instalado; root do projeto Java (Maven/Gradle) ou Go no
disco.

## Passo a passo

```bash
apiforge analyze --project . --fail-on high   # descoberta + case persistido
apiforge next-step                             # rota recomendada por evidência
```

Num host agentic, a skill `api-forge-discovery` conduz a mesma passada
com o API-IR e proveniência file:line.

## Saída esperada / interpretação

API-IR + findings persistidos em `.apiforge/case/` — rotas detectadas do
código com âncora, frameworks identificados, lacunas `unresolved`
declaradas.

## Verificação

Rotas devem carregar âncora de código (arquivo:linha); ausência de
âncora = declaração `unresolved`, nunca rota inventada.

## Limitações

Análise estática: rotas registradas por reflexão, plugins ou config
externa podem não aparecer — o IR declara como não-resolvido.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| framework errado | multi-framework no repo | escopo do módulo via `--project` |
| poucas rotas | rotas via config externa | ver `unresolved`; descoberta não supõe |

## Uso por agentes

`api-forge-discovery` é a primeira skill do roteador para repo novo —
a saída já é o IR canônico que os demais especialistas consomem.
