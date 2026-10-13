# Gremlin — padrões, anti-padrões e regras

Carregue quando um call site Gremlin gerou finding ou quando for revisar
uma traversal. O analisador do API Forge lê **o texto da traversal**
(steps de topo, na ordem escrita); não executa nada. Em Python o encadeamento
multi-linha é resolvido pela AST; em Java/Go/TS por junção de linhas
(`AF-GDB-HEURISTIC`).

## Sumário

- Mapa regra ↔ anti-padrão
- O que conta como limite
- Execução nativa no Neptune
- Paginação, dedup e explosão de caminhos
- Parâmetros em vez de concatenação
- Fontes

## Mapa regra ↔ anti-padrão

| Regra | Anti-padrão | Correção |
|---|---|---|
| AF-GDB-001 | `repeat(out('KNOWS'))` sem `times()`/`until()` | `repeat(out('KNOWS')).times(3)` ou `.until(hasId(x)).limit(1)`; mantenha `simplePath()` quando ciclos importam |
| AF-GDB-002 | `out()`, `in()`, `both()`, `outE()`, `inE()`, `bothE()` sem label | `out('OWNS')`; no Neptune o explain mostra o aviso de predicados para traversal sem label (AF-GDB-022 no plano) |
| AF-GDB-003 | `g.V()`/`g.E()` sem id e sem `hasLabel`/`has`/`hasId` logo depois | `g.V(id)` ou `g.V().hasLabel('User').has('email', e)` |
| AF-DATA-013 | traversal terminal sem `limit()`, `range()`, `tail()`, `next()`, `count()` | `limit(n)`/`range(a, b)` ou terminal único (`next()`) |
| AF-GDB-008 | texto da query montado em runtime (f-string, `+`, `String.format`, template) | traversal fluente (GLV) ou script parametrizado com bindings |

Exemplos (Python, gremlin_python):

```python
# AF-GDB-003 + AF-GDB-002 + AF-DATA-013
g.V().out().values("name").toList()

# corrigido
g.V().hasLabel("User").has("userId", uid).out("FOLLOWS").limit(50).values("name").toList()

# AF-GDB-001
g.V(uid).repeat(__.out("KNOWS")).emit().toList()

# corrigido: profundidade declarada e resultado limitado
g.V(uid).repeat(__.out("KNOWS").simplePath()).times(2).dedup().limit(100).toList()
```

## O que conta como limite

- Limitam: `limit`, `range`, `tail`, `next`, `count`, `hasNext` em
  qualquer posição de topo da cadeia.
- Não limitam: `toList()`, `iterate()`, `fold()`, `dedup()`, `order()`.
- Limite **dentro** de traversal anônima (`local(out().limit(5))`) controla
  fan-out por elemento, não o tamanho do resultado; o analisador não o
  conta como bound de topo.
- `count()` limita o retorno, não o trabalho: `g.V().count()` ainda lê
  todos os vértices — combine com AF-GDB-003.

## Execução nativa no Neptune

O Neptune converte a traversal em operadores próprios; o que não converte é
executado pela engine TinkerPop, com perda grande de desempenho a partir
daquele ponto.

- O explain mostra `Original Traversal`, `Converted Traversal` e
  `Optimized Traversal`; um step não convertido aparece como
  `WARNING: >> <step> << (or one of its children) is not supported natively yet`
  → AF-GDB-020.
- Lambdas, `sideEffect` com closures, alguns usos de `fold()`/`unfold()`,
  `math()`, `match()` e `subgraph()` estão entre os suspeitos habituais; a
  lista muda por versão de engine — confie no explain da sua versão, não em
  lista decorada.
- Mova filtros para antes do step não nativo e evite `fold()` no meio da
  traversal só para reagrupar.
- O query hint `useDFE` direciona a traversal para o engine DFE quando
  habilitado; o texto do explain pode mudar. Se o import falhar com
  `AF-GDB-PLAN-PARSE`/`AF-GDB-PLAN-FORMAT`, guarde o dump e declare o gap.

## Paginação, dedup e explosão de caminhos

- Paginação: `order().by('createdAt', desc).range(offset, offset + size)`.
  `range` com offset alto ainda percorre o prefixo; para listas grandes use
  cursor por chave (`has('createdAt', lt(cursor)).limit(size)`).
- `dedup()` cedo reduz frontier em grafos com muitos caminhos para o mesmo
  vértice; tarde, só limpa o resultado depois do trabalho feito.
- `path()` e `simplePath()` guardam histórico por traverser: custo de
  memória proporcional ao número de caminhos, não de vértices.
- Explosão: com grau médio *b* e profundidade *d*, o frontier é da ordem de
  *b^d* (50 vizinhos, 3 saltos ≈ 125 000 traversers). Ver `performance.md`.

## Parâmetros em vez de concatenação

- Texto dinâmico (`"g.V('" + id + "')"`) é injeção de Gremlin e impede cache
  de compilação do script no servidor. O API Forge marca `query_dynamic`,
  emite `AF-GDB-DYNAMIC-QUERY` e AF-GDB-008; `bounded` vira `unresolved`
  quando nenhum step de limite é visível.
- Use a API fluente (GLV: gremlin_python, gremlin-go, gremlin-javascript,
  Java) — os valores viajam como bytecode/argumentos, não como script.
- Em submissão por script (`client.submit(script, bindings)`), passe
  valores em `bindings`; nunca formate o script.
- A análise de exploração de injeção pertence a `api-security-reviewer`.

## Mutação

`addV`, `addE`, `drop`, `property`, `mergeV`, `mergeE` marcam `mutation`.
O collector recusa explain/profile de traversal com mutação
(`AF-GDB-PROFILE-MUTATION`) — o API Forge nunca envia escrita ao banco.

## Fontes

- TinkerPop reference — repeat/times/until: https://tinkerpop.apache.org/docs/current/reference/#repeat-step
- TinkerPop reference — limit/range/tail: https://tinkerpop.apache.org/docs/current/reference/#range-step
- TinkerPop — bindings e GLVs: https://tinkerpop.apache.org/docs/current/reference/#gremlin-drivers-variants
- Neptune — Gremlin explain: https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-explain-api.html
- Neptune — suporte nativo a steps: https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-step-support.html
- Neptune — query hints Gremlin: https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-query-hints.html
