# Neo4j — referência

Carregue quando o vendor detectado for Neo4j. O API Forge **não tem
coletor** para Neo4j: análise estática do código (`model neo4j-access` ou
`model graph-access`) e planos importados de dump
(`model graph-explain --format neo4j-explain|neo4j-profile`). Índices e
constraints abaixo são conhecimento para formular perguntas — o API Forge
nunca os cria.

## Sumário

- Drivers e como o extractor os reconhece
- Dialeto Cypher
- Índices e constraints
- EXPLAIN e PROFILE
- Transações e roteamento
- Fontes

## Drivers e como o extractor os reconhece

| Linguagem | Pacote | Chamadas que carregam query |
|---|---|---|
| Python | `neo4j` | `driver.execute_query(q, params, database_=...)`, `session.run(q, params)`, `tx.run(...)` em `session.execute_read/execute_write` |
| Java | `org.neo4j.driver` | `driver.executableQuery(q).withParameters(...).execute()`, `session.run(q, params)`, `tx.run(...)` |
| Go | `github.com/neo4j/neo4j-go-driver/v5/neo4j` | `neo4j.ExecuteQuery(ctx, driver, q, params, neo4j.EagerResultTransformer)`, `session.Run(ctx, q, params)` |
| JavaScript/TypeScript | `neo4j-driver` | `driver.executeQuery(q, params)`, `session.run(q, params)`, `tx.run(...)` |

Boas práticas que o finding costuma citar:

- Parâmetros sempre (`$name`); texto montado → AF-GDB-008.
- `execute_query`/`executeQuery` gerenciam retry de transação transitória;
  `session.run` em auto-commit não. Política de retry é de
  `api-resilience-engineer`.
- `routing_` / `RoutingControl.READ` envia leitura a secundários no
  cluster; leitura-após-escrita usa bookmarks.
- Feche sessões/drivers; um driver por processo.
- Java/Go/TS são lidos por regex com junção de linhas
  (`AF-GDB-HEURISTIC`); Python pela AST.

## Dialeto Cypher

- Neo4j 5: `elementId()` substitui `id()`; quantified path patterns
  `((a)-[:R]->(b)){1,3}` e `SHORTEST k` além de `[*a..b]`.
- `CALL { ... } IN TRANSACTIONS OF n ROWS` para lotes (escrita = mutação).
- APOC/GDS são extensões; query que depende delas não porta para Neptune.
- `MATCH (n)` sem label → `AllNodesScan` (AF-GDB-005 no código,
  AF-GDB-024 no plano).
- Padrões por vírgula sem variável comum → `CartesianProduct`
  (AF-GDB-006 / AF-GDB-024).
- Diferenças com Neptune em `opencypher.md`.

## Índices e constraints

Somente conhecimento; a decisão e a DDL são do time dono do banco.

| Tipo | Exemplo | Serve para |
|---|---|---|
| Range | `CREATE INDEX user_email FOR (u:User) ON (u.email)` | igualdade/intervalo em propriedade |
| Text | `CREATE TEXT INDEX ... ON (p.name)` | `CONTAINS`/`ENDS WITH` |
| Point | `CREATE POINT INDEX ...` | distância espacial |
| Full-text | `CREATE FULLTEXT INDEX ...` | busca Lucene via procedure |
| Vector | `CREATE VECTOR INDEX ...` | similaridade (`db.index.vector.queryNodes(idx, k, emb)`; `k` é o teto) |
| Unicidade | `CREATE CONSTRAINT FOR (u:User) REQUIRE u.userId IS UNIQUE` | chave natural; torna `MERGE` seguro sob concorrência |

Índice em relacionamento existe (`FOR ()-[r:RATED]-() ON (r.score)`) e é o
equivalente a filtro vertex-centric para supernós. Pergunta útil no
relatório: "a propriedade usada como âncora tem índice ou constraint?" —
resposta vem de `SHOW INDEXES`/`SHOW CONSTRAINTS` exportado, não do código.

## EXPLAIN e PROFILE

- `EXPLAIN` não executa; mostra operadores e `Estimated Rows`.
- `PROFILE` executa; adiciona `Rows`, `DB Hits`, cache hits/misses e
  memória. Rode em ambiente não produtivo ou réplica; é execução real.
- Exporte o texto do Browser/`cypher-shell` ou o `ResultSummary.plan`
  / `.profile` do driver e importe com `model graph-explain`.
- Leitura e mapeamento para AF-GDB-024/025 em `plans.md`.

## Transações e roteamento

- Leitura em `execute_read` pode ir a réplica; escrita em `execute_write`
  vai ao líder.
- Transação longa segura locks de escrita e memória; lote grande em
  `IN TRANSACTIONS` controla o tamanho.
- Timeouts de transação (`dbms.transaction.timeout` / `timeout` no driver)
  são configuração; valores ficam com `api-resilience-engineer`.

## Fontes

- Neo4j Python Driver Manual: https://neo4j.com/docs/python-manual/current/
- Neo4j Java Driver Manual: https://neo4j.com/docs/java-manual/current/
- Neo4j Go Driver Manual: https://neo4j.com/docs/go-manual/current/
- Neo4j JavaScript Driver Manual: https://neo4j.com/docs/javascript-manual/current/
- Cypher Manual — índices: https://neo4j.com/docs/cypher-manual/current/indexes/
- Cypher Manual — constraints: https://neo4j.com/docs/cypher-manual/current/constraints/
- Cypher Manual — execution plans: https://neo4j.com/docs/cypher-manual/current/planning-and-tuning/execution-plans/
- Cypher Manual — CALL IN TRANSACTIONS: https://neo4j.com/docs/cypher-manual/current/subqueries/subqueries-in-transactions/
