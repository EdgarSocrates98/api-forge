# Receita — inventariar uma API sem contrato OpenAPI mantido

**O quê:** `apiforge discover` inventaria estaticamente as rotas de um
projeto FastAPI sem executar código; para Java/Go e outros stacks a
descoberta é conduzida pela skill `api-forge-discovery`, que mapeia
linguagem, framework, rotas, handlers, schemas, auth, dependências,
bancos, filas, IaC, testes e telemetria num API-IR com proveniência.
**Por que:** sem OpenAPI mantido, o contrato real é o código — e a
descoberta determinística nunca executa o projeto.
**Quando:** repo desconhecido, inventário de rotas, migração ou revisão
sem contrato de origem.
**Quando não:** o OpenAPI já existe e é mantido — então
`apiforge analyze --contract` é o caminho direto (ver
[analyze-contract](analyze-contract.md)).

## Problema

"Não há `openapi.yaml` — como inventariar as rotas sem chutar?"

## Pré-requisitos

`apiforge` instalado; root do projeto no disco. Para `discover` via CLI:
projeto FastAPI.

## Passo a passo

```bash
# FastAPI — inventário de rotas direto, com cache por hash
apiforge discover --project .

# demais stacks — a skill api-forge-discovery no host conduz
# a extração do API-IR com âncoras arquivo:linha
```

Com um OpenAPI gerado depois (FastAPI expõe `/openapi.json`), o caminho
vira `apiforge analyze --contract` (receita
[analyze-contract](analyze-contract.md)) — lembrando que `--out-dir`
fica **fora** do projeto analisado.

## Saída esperada / interpretação

`discover`: JSON com `routes` (facts com âncora), `diagnostics` e
`input_hashes`. Skill: API-IR com proveniência e lacunas declaradas
`unresolved`.

## Verificação

Rotas carregam âncora de código (arquivo:linha); ausência de âncora é
`unresolved` declarado, nunca rota inventada.

## Limitações

`discover` via CLI cobre FastAPI; Java (Spring), Go e outros frameworks
passam pela skill `api-forge-discovery`. Análise estática: rotas por
reflexão/config externa podem não aparecer — declarado, não escondido.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| `discover` vazio | projeto não-FastAPI | use a skill `api-forge-discovery` |
| `AF-INPUT-NOT-FOUND` | `--project` aponta arquivo | aponte o diretório root |

## Uso por agentes

`api-forge-discovery` é a primeira skill do roteador para repo novo —
a saída já é o IR canônico que os demais especialistas consomem.
