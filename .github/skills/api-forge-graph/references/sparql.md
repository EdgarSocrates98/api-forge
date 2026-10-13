# SPARQL — padrões, anti-padrões e regras

Carregue quando um call site SPARQL (Neptune RDF) gerou finding. O
analisador remove comentários e literais, descarta `SELECT *` e `COUNT(*)`
e só então procura modificadores de property path; não executa nada.

## Sumário

- Mapa regra ↔ anti-padrão
- O que conta como limite
- OPTIONAL e FILTER
- Updates são mutação
- Named graphs no Neptune
- Explain de SPARQL no API Forge
- Fontes

## Mapa regra ↔ anti-padrão

| Regra | Anti-padrão | Correção |
|---|---|---|
| AF-GDB-007 | property path ilimitado: `?a ex:knows+ ?b`, `?c rdfs:subClassOf* ?d`, `(ex:p/ex:q)+` | profundidade explícita com sequência (`ex:knows/ex:knows`), `UNION` de 1..n saltos ou hierarquia materializada |
| AF-DATA-013 | `SELECT` sem `LIMIT` | `LIMIT n` (ou `ASK`, ou `SELECT (COUNT(...) AS ?n)`) |
| AF-GDB-008 | query montada por concatenação de IRIs/literais | `VALUES` com valores validados ou bindings do cliente |

```sparql
# AF-GDB-007 + AF-DATA-013
SELECT ?friend WHERE { <urn:u:1> ex:knows+ ?friend }

# corrigido: até 2 saltos, resultado limitado
SELECT DISTINCT ?friend WHERE {
  { <urn:u:1> ex:knows ?friend }
  UNION
  { <urn:u:1> ex:knows/ex:knows ?friend }
}
LIMIT 100
```

`p?` (zero ou um) é limitado e não dispara. A forma `p{n,m}` aparecia em
rascunhos do SPARQL 1.1 mas **não** está na recomendação final; não conte
com ela no Neptune.

`rdfs:subClassOf*` sobre ontologia pequena e estável é aceitável quando o
volume é conhecido — o finding continua válido como pergunta; a prova de
que é barato vem do plano (`model graph-explain`).

## O que conta como limite

- `LIMIT n` em qualquer ponto.
- `ASK` (devolve booleano).
- `SELECT` cuja projeção é só `(COUNT(...) AS ?x)`.
- `OFFSET` sozinho não limita. Paginação `ORDER BY ?k LIMIT n OFFSET m`
  exige ordenação total; offset alto materializa o prefixo — prefira
  cursor por chave (`FILTER(?createdAt < ?cursor)`).
- `CONSTRUCT`/`DESCRIBE` sem `LIMIT` podem devolver grafos inteiros.

## OPTIONAL e FILTER

- `FILTER` restringe a solução do grupo em que está; posicione-o no grupo
  mais interno possível para que o engine filtre cedo. `FILTER` no topo
  depois de vários `OPTIONAL` avalia sobre o produto completo.
- `OPTIONAL` faz left join: vários `OPTIONAL` independentes sobre o mesmo
  sujeito multiplicam linhas (um por combinação de valores). Agrupe com
  `GROUP_CONCAT` ou consulte em separado.
- `FILTER NOT EXISTS { }` costuma ser mais claro que
  `OPTIONAL { } FILTER(!bound(?x))`; o custo real só aparece no plano.
- Padrões de tripla sem variável compartilhada no mesmo grupo produzem
  produto cartesiano — o mesmo problema de AF-GDB-006, sem regra estática
  dedicada em SPARQL; aparece no plano.

## Updates são mutação

`INSERT DATA`, `INSERT { } WHERE`, `DELETE DATA`, `DELETE { } WHERE`,
`DELETE WHERE`, `LOAD`, `CLEAR`, `DROP`, `CREATE GRAPH`, `ADD`, `MOVE` e
`COPY` marcam `mutation`. O API Forge nunca envia update; o endpoint
SPARQL do Neptune aceita updates no mesmo serviço, então separar papéis de
IAM (`neptune-db:ReadDataViaQuery` vs escrita) é decisão de infra
(`api-infra-reviewer`).

## Named graphs no Neptune

- Neptune armazena quads. Tripla inserida sem `GRAPH` vai para o named
  graph padrão `http://aws.amazon.com/neptune/vocab/v01/DefaultNamedGraph`.
- Query sem `FROM`/`FROM NAMED` enxerga a união de todos os named graphs;
  use `GRAPH <g> { }` ou `FROM <g>` para escopo explícito — reduz volume e
  evita misturar tenants/versões.
- Named graph por tenant ou por fonte facilita `DROP GRAPH` controlado e
  proveniência, mas consulta cross-graph fica mais cara.

## Explain de SPARQL no API Forge

O Neptune expõe explain de SPARQL via parâmetro `explain=static|dynamic|details`
no endpoint HTTP, mas `neptunedata` não tem operação de explain SPARQL.
Por isso `collect neptune-explain --language sparql` é recusado com
`AF-GDB-EXPLAIN-SPARQL`; rode o explain (preferencialmente `static`, que
não executa) pelo seu cliente e importe com
`model graph-explain --path <dump> --format neptune-sparql-explain`. Leitura
do plano em `plans.md`.

## Fontes

- W3C SPARQL 1.1 Query — property paths: https://www.w3.org/TR/sparql11-query/#propertypaths
- W3C SPARQL 1.1 Query — OPTIONAL e FILTER: https://www.w3.org/TR/sparql11-query/#optionals
- W3C SPARQL 1.1 Update: https://www.w3.org/TR/sparql11-update/
- Neptune — SPARQL explain: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-explain-using.html
- Neptune — default graph e named graphs: https://docs.aws.amazon.com/neptune/latest/userguide/feature-sparql-compliance.html
- Neptune — query hints SPARQL: https://docs.aws.amazon.com/neptune/latest/userguide/sparql-query-hints.html
