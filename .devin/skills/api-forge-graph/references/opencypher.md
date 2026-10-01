# openCypher — padrões, anti-padrões e dialetos

Carregue quando um call site openCypher/Cypher gerou finding, ou quando a
mesma query precisa rodar em Neptune e Neo4j. O analisador lê o texto da
query com literais em branco; não executa nada.

## Sumário

- Mapa regra ↔ anti-padrão
- O que conta como limite
- Paginação e parâmetros
- Mutação
- Neptune vs Neo4j
- Fontes

## Mapa regra ↔ anti-padrão

| Regra | Anti-padrão | Correção |
|---|---|---|
| AF-GDB-004 | path de tamanho variável aberto: `[*]`, `[:KNOWS*]`, `[*2..]` | teto explícito: `[:KNOWS*1..3]`; em Neo4j 5, quantified path `((a)-[:KNOWS]->(b)){1,3}` |
| AF-GDB-005 | nenhum nó do `MATCH` ancorado: `MATCH (n) WHERE n.email = $e` | `MATCH (n:User {email: $e})`; âncora = label, mapa de propriedades ou variável já ligada |
| AF-GDB-006 | padrões separados por vírgula sem variável comum: `MATCH (a:User), (b:Product)` | conectar por relação ou ligar via `WITH`; produto cartesiano só se intencional e limitado |
| AF-DATA-013 | sem `LIMIT` e `RETURN` não agregado | `LIMIT $size` ou `RETURN count(*)` |
| AF-GDB-008 | texto montado por concatenação/template | parâmetros `$nome` |
| AF-GDB-009 | `CALL neptune.algo.*` sem `MATCH` anterior que escope a entrada (Analytics) | ver `performance.md` |
| AF-GDB-010 | `CALL neptune.algo.vectors.*` sem `topK` | ver `performance.md` |

Exemplos:

```cypher
// AF-GDB-005 + AF-GDB-004 + AF-DATA-013
MATCH (a)-[:KNOWS*]->(b) WHERE a.userId = $uid RETURN b

// corrigido
MATCH (a:User {userId: $uid})-[:KNOWS*1..2]->(b:User)
RETURN DISTINCT b.userId LIMIT 50

// AF-GDB-006: cartesiano User × Product
MATCH (u:User {userId: $uid}), (p:Product) RETURN u, p

// corrigido: relação explícita
MATCH (u:User {userId: $uid})-[:BOUGHT]->(p:Product) RETURN p.sku LIMIT 20
```

Path sem `*` (`-[:KNOWS]->`) é um salto e não é AF-GDB-004. `[*3]` (exato)
e `[*1..3]` (fechado) passam; `[*]`, `[*..]` e `[*2..]` disparam.

## O que conta como limite

- `LIMIT <n>` ou `LIMIT $param` em qualquer ponto da query.
- `RETURN` composto só de agregações (`count`, `sum`, `avg`, `min`, `max`).
- `SKIP` sozinho **não** limita.
- `LIMIT` dentro de subquery/`WITH` intermediário limita o frontier daquela
  etapa — útil contra supernó (`WITH u ORDER BY u.score DESC LIMIT 100`).

## Paginação e parâmetros

- `ORDER BY ... SKIP $offset LIMIT $size` é estável só com ordenação total
  (desempate por chave única). Offset alto ainda materializa o prefixo;
  prefira cursor (`WHERE n.createdAt < $cursor ORDER BY n.createdAt DESC LIMIT $size`).
- Parâmetros: Neo4j `$param` nos drivers (`execute_query(q, params)`);
  Neptune aceita `parameters` (JSON) no endpoint openCypher HTTPS e no
  `neptunedata.execute_open_cypher_query`. Parâmetro protege contra
  injeção e permite reuso de plano.
- Labels e tipos de relação não são parametrizáveis em Cypher padrão; se o
  label vem de input, valide contra allowlist no código (o API Forge marca
  o texto como dinâmico).

## Mutação

`CREATE`, `MERGE`, `SET`, `DELETE`, `DETACH DELETE` e `REMOVE` marcam
`mutation`. O collector recusa explain de query com mutação
(`AF-GDB-PROFILE-MUTATION`). `MERGE` sem chave única/constraint é corrida
de duplicata em escrita concorrente — pergunta para o design, não finding
automático.

## Neptune vs Neo4j

| Tema | Neptune (Database/Analytics) | Neo4j 5 |
|---|---|---|
| Ids | `id(n)` string; `~id` definível na criação | `elementId(n)`; `id()` deprecado |
| Procedures | só `neptune.*` (ex.: `neptune.algo.*` no Analytics); sem APOC/GDS | APOC, GDS, `db.*` |
| Índices/constraints | sem DDL Cypher; índices gerenciados pelo serviço | `CREATE INDEX`, `CREATE CONSTRAINT` |
| Paths quantificados | `[*a..b]` | `[*a..b]` e quantified path patterns |
| Plano | `explain` = `static`/`dynamic`/`details` via parâmetro HTTP | `EXPLAIN`/`PROFILE` como prefixo |
| Transação | uma requisição HTTP = uma transação | sessões, `execute_read`/`execute_write` |
| Multi-label | suportado | suportado |

Query portável: labels explícitos, parâmetros, `LIMIT`, paths fechados,
nenhuma procedure de vendor. Mesmo assim os planos diferem — avalie com o
plano de cada engine.

## Fontes

- openCypher (especificação): https://opencypher.org/resources/
- Neptune — openCypher: https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-opencypher.html
- Neptune — conformidade e diferenças openCypher: https://docs.aws.amazon.com/neptune/latest/userguide/feature-opencypher-compliance.html
- Neptune — parâmetros openCypher: https://docs.aws.amazon.com/neptune/latest/userguide/opencypher-parameterized-queries.html
- Neo4j Cypher Manual — variable-length e quantified paths: https://neo4j.com/docs/cypher-manual/current/patterns/variable-length-patterns/
- Neo4j Cypher Manual — parâmetros: https://neo4j.com/docs/cypher-manual/current/syntax/parameters/
