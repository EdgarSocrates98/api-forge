# Planos de execução — leitura por formato

Carregue quando houver dump de explain/profile para ler ou importar. Plano
é a única fonte de cardinalidade no API Forge: call site sem plano
importado mantém cardinalidade `unresolved`.

## Sumário

- Importar
- Executa ou não executa
- Neptune Gremlin explain
- Neptune Gremlin profile
- Neptune openCypher explain
- Neptune SPARQL explain
- Neo4j EXPLAIN e PROFILE
- Regra de fan-out (AF-GDB-025)
- Fontes

## Importar

```text
apiforge model graph-explain --path <arquivo> [--format <fmt>] [--synthetic]
```

`--format` (auto-detectado pelo cabeçalho quando omitido):
`neptune-gremlin-explain`, `neptune-gremlin-profile`,
`neptune-opencypher-static`, `neptune-opencypher-dynamic`,
`neptune-sparql-explain`, `neo4j-explain`, `neo4j-profile`.

Saída: `GraphPlanIR` (formato, `executed`, `source_sha256`, operadores com
`units_in`/`units_out`/`estimate`/`native`, avisos, `predicate_count`).
Formato não reconhecido → `AF-GDB-PLAN-FORMAT` (passe `--format`); texto
ilegível → `AF-GDB-PLAN-PARSE` com linha. `--synthetic` marca o IR como
sintético: serve a teste e exemplo, **nunca** a evidência de campo.

## Executa ou não executa

| Formato | Executa a query? |
|---|---|
| Neptune Gremlin `explain` | não |
| Neptune Gremlin `profile` | **sim** |
| Neptune openCypher `explain=static` | não |
| Neptune openCypher `explain=dynamic` / `details` | **sim** |
| Neptune SPARQL `explain=static` | não |
| Neptune SPARQL `explain=dynamic` / `details` | **sim** |
| Neo4j `EXPLAIN` | não |
| Neo4j `PROFILE` | **sim** |

Plano executado traz contagens reais; plano estático traz só estrutura e
estimativas. O `GraphPlanIR.executed` registra qual dos dois foi lido.

## Neptune Gremlin explain

Seções: `Original Traversal` (como escrita), `Converted Traversal` (o que
virou operador Neptune), `Optimized Traversal` (após reordenação de joins),
depois `Predicates` e avisos.

| Sinal no texto | Regra |
|---|---|
| step fora da `Converted Traversal` + `WARNING: >> <step> << (or one of its children) is not supported natively yet` | AF-GDB-020 (step não nativo; o resto da traversal roda em TinkerPop) |
| `estimatedCardinality=INFINITY` ou `rangeCountEstimate=9223372036854775807` (Long.MAX) | AF-GDB-021 (estimativa ilimitada: padrão sem predicado seletivo) |
| aviso com `# of predicates` (traversal reversa/sem label, ex. `in()`/`both()` sem label) | AF-GDB-022 |

Correção típica: label e `has()` seletivo antes do step problemático;
substituir step não nativo por equivalente suportado; `limit()` cedo.

## Neptune Gremlin profile

Executa a traversal e devolve, além das seções do explain, `Physical
Pipeline`, `Runtime (ms)`, `Traversal Metrics` (contagem e tempo por step)
e `Index Operations` (consultas a índice e contagens). Leia nessa ordem:
o step com maior tempo acumulado, depois a razão saída/entrada desse step,
depois os avisos herdados do explain (020/021/022 também valem aqui).
Coletar via API Forge só com `collect neptune-explain --profile` (ver
`neptune.md`).

## Neptune openCypher explain

Parâmetro `explain` no endpoint openCypher:

- `static` — não executa; mostra operadores DFE e argumentos.
- `dynamic` — executa; adiciona `Units In`, `Units Out`, `Ratio`, `Time (ms)`.
- `details` — executa; como `dynamic` com detalhes de argumentos.

Tabela por operador: `ID`, `Out #1`, `Out #2`, `Name`, `Arguments`, `Mode`,
`Units In`, `Units Out`, `Ratio`, `Time (ms)`.

| Sinal | Regra |
|---|---|
| `DFEPipelineScan` com `label 'ALL'` nos argumentos (scan sem label) | AF-GDB-023 |
| operador com `Units Out / Units In ≥ 1000` (só modos executados) | AF-GDB-025 |

`DFEPipelineScan` com label específico é normal; com `'ALL'` significa
padrão de nó sem label — a mesma raiz de AF-GDB-005 no código.

## Neptune SPARQL explain

Parâmetro `explain=static|dynamic|details` no endpoint SPARQL (saída
`text/plain`, `text/html` ou `text/csv`). Mesma tabela de operadores
(`Units In`/`Units Out`/`Ratio` só nos modos executados). Leia scans de
padrão sem constante (`?s ?p ?o`), joins com razão alta e `Projection`
tardia. Via collector é recusado (`AF-GDB-EXPLAIN-SPARQL`): importe o dump.

## Neo4j EXPLAIN e PROFILE

- `EXPLAIN <query>` — não executa; árvore de operadores com
  `Estimated Rows`.
- `PROFILE <query>` — executa; adiciona `Rows`, `DB Hits`, page cache
  hits/misses e memória por operador.

| Operador | Regra |
|---|---|
| `AllNodesScan` | AF-GDB-024 (nenhum label no ponto de partida) |
| `CartesianProduct` | AF-GDB-024 (padrões desconectados; ver AF-GDB-006) |
| `Expand(All)` com `Rows` ≫ entrada (PROFILE) | AF-GDB-025 se razão ≥ 1000 |

Preferíveis: `NodeIndexSeek`/`NodeUniqueIndexSeek` > `NodeByLabelScan` >
`AllNodesScan`. Exporte o plano como texto ou JSON do driver
(`ResultSummary.plan`/`.profile`) para importar.

## Regra de fan-out (AF-GDB-025)

Em plano executado, operador com `Units Out / Units In ≥ 1000` (ou `Rows`
do operador sobre `Rows` do filho, em Neo4j) indica expansão explosiva —
forte indício de supernó ou falta de filtro de aresta. É dica, não prova
de supernó: confirme o grau do vértice antes de propor mudança de modelo
(`modeling.md`). Em plano estático a regra não dispara.

## Fontes

- Neptune — Gremlin explain: https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-explain-api.html
- Neptune — Gremlin profile: https://docs.aws.amazon.com/neptune/latest/userguide/gremlin-profile-api.html
- Neptune — openCypher explain: https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-opencypher-explain.html
- Neptune — SPARQL explain: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-explain-using.html
- Neo4j Cypher Manual — execution plans: https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/execution-plans/
- Neo4j Cypher Manual — operators: https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/operators/
