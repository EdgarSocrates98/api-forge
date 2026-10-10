# Receita — consultar o grafo de proveniência do case

**O quê:** `apiforge graph` é o grafo de proveniência nativo —
`graph build` popula `nodes.jsonl`/`edges.jsonl` dos artefatos do case,
`graph query` filtra por vocabulário fechado, `graph impact` faz
travessia reversa.
**Por que:** "o que essa mudança afeta?" é uma pergunta de grafo — a
resposta sai dos edges reais do case, não de releitura.
**Quando:** análise de impacto, rastrear a origem de um finding,
correlacionar artefatos do case.
**Quando não:** grafo do sistema para Neptune/Neo4j — aí é a skill
`api-forge-graph` com `GraphAccessIR` (dados, não proveniência).

## Problema

"Esse endpoint muda — quais artefatos/findings dependem dele?"

## Pré-requisitos

Um case persistido (`.apiforge/case/case.json`) — o grafo constrói de
artefatos reais, nunca de texto.

## Passo a passo

```bash
apiforge graph build --case .apiforge/case --out .apiforge/graph
apiforge graph query --dir .apiforge/graph --kind route
apiforge graph impact --dir .apiforge/graph --node <node_id>
```

## Saída esperada / interpretação

Nós e edges JSONL determinísticos; `query` filtra por kind/fechado;
`impact` devolve tudo que depende transitivamente do nó.

## Verificação

O `ForgeGraphView` (projeção `graphview`) renderiza os mesmos nós —
divergência entre query e view é bug, reportável.

## Limitações

Vocabulário fechado: `query` não aceita texto livre; nó fora do grafo
retorna `unresolved`, nunca vizinho inventado.

## Erros comuns

| Sintoma | Causa | Ação |
|---|---|---|
| grafo vazio | `graph build` sem case | rode `analyze`/`task` primeiro |
| `impact` vazio | nó folha sem dependentes | confirme o `node_id` no `query` |

## Uso por agentes

`workspace_graph` e o gateway `apiforge_expand` navegam o mesmo grafo —
o agente entrega `node_id`s, não releituras.
