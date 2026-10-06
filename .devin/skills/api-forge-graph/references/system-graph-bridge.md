# Ponte com o grafo do sistema

Carregue quando o grafo do próprio API Forge (`graph build`: endpoints,
handlers, stores, findings, evidências) precisar ir para um graph store,
ou quando for comparar o `DomainGraphSketch` extraído do código com o
design. Códigos `AF-GRAPH-*` (`AF-GRAPH-FORMAT`, `AF-GRAPH-NOT-FOUND`, …)
pertencem a este grafo do sistema — não confunda com `AF-GDB-*` de bancos
de grafo.

## Sumário

- `graph export` por formato
- Formato `neptune` (CSV do bulk loader)
- Formato `rdf` (N-Triples)
- Determinismo e digests
- Carregar no Neptune
- Consultar com cast
- DomainGraphSketch
- Fontes

## `graph export` por formato

```text
apiforge graph export --format jsonl     # padrão: nodes/edges JSONL
apiforge graph export --format neptune   # vertices.csv + edges.csv
apiforge graph export --format rdf       # graph.nt
```

Formato desconhecido → `AF-GRAPH-FORMAT`; grafo ausente →
`AF-GRAPH-NOT-FOUND` (rode `graph build` antes). Export só escreve
arquivos locais; não fala com banco algum.

## Formato `neptune` (CSV do bulk loader)

Cabeçalhos no formato CSV Gremlin do loader do Neptune (`format: csv`):

`vertices.csv`

```text
~id,~label,<prop>:String,<prop>:String,...
```

`edges.csv`

```text
~id,~from,~to,~label,<prop>:String,...
```

- Cabeçalho = união das chaves de propriedade, colunas ordenadas.
- **Toda** propriedade é `:String` — o export não adivinha tipos (decisão
  "declarado, nunca inferido"). Valor aninhado vira JSON serializado.
- Célula vazia = propriedade ausente naquele elemento (o loader não cria
  a propriedade), não string vazia com significado.
- `~id` de aresta é estável: derivado de (origem, destino, tipo) — reexport
  do mesmo grafo produz os mesmos ids, e recarga com o mesmo id atualiza
  em vez de duplicar.

## Formato `rdf` (N-Triples)

`graph.nt`, uma tripla por linha, linhas ordenadas:

```text
<urn:apiforge:node:ID> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <urn:apiforge:kind:KIND> .
<urn:apiforge:node:FROM> <urn:apiforge:edge:KIND> <urn:apiforge:node:TO> .
<urn:apiforge:node:ID> <urn:apiforge:prop:KEY> "valor" .
```

- IRIs no namespace `urn:apiforge:` (`node:`, `edge:`, `kind:`, `prop:`),
  com percent-encoding; literais com escape N-Triples, todos como string
  simples.
- RDF puro não tem propriedade em aresta sem reificação: confira no
  `graph.nt` gerado se as propriedades de aresta de que a consulta precisa
  estão presentes antes de depender delas; se não, use o formato `neptune`.

## Determinismo e digests

Saída byte-determinística para o mesmo grafo de entrada. `export.json`
registra o formato e o digest de cada arquivo escrito; compare digests para
provar que o arquivo carregado é o exportado (correspondência, não autoria).

## Carregar no Neptune

Carga é mutação e fica com o operador:

1. Copie os arquivos para um bucket S3 na mesma região do cluster.
2. Garanta IAM role associado ao cluster com leitura no bucket e VPC
   endpoint de S3 (`neptune.md`).
3. Dispare o loader com `format: csv` (property graph) ou
   `format: ntriples` (RDF) e acompanhe o status do job.
4. Property graph e RDF não se enxergam no Neptune: escolha o formato pelo
   tipo de consulta (Gremlin/openCypher vs SPARQL).

## Consultar com cast

Como tudo é string, comparação numérica precisa de conversão (label e
propriedade abaixo são ilustrativos — use os nomes do seu `vertices.csv`):

```cypher
MATCH (f:finding) WHERE toInteger(f.line) >= 100 RETURN f LIMIT 50
```

Prefira openCypher (`toInteger`, `toFloat`): Gremlin não tem cast de
string para número sem lambda, e o Neptune não aceita lambdas. Em SPARQL
use `xsd:integer(?v)` dentro de `FILTER`. Comparar strings
lexicograficamente (`"9" > "10"`) é o erro silencioso típico.

## DomainGraphSketch

Emitido por `model graph-access` junto com o `GraphAccessIR`:

- `vertex_labels` — labels vistos no código (`hasLabel`, `addV`, `(:Label)`,
  `?x a <Class>`);
- `edge_labels` — labels de aresta vistos (`out('X')`, `[:X]`, `addE`);
- `edges` — triplas (origem, label, destino) quando o código as declara
  juntas; lado desconhecido = `null`;
- `evidence` — caminhos de arquivo/linha que sustentam cada item.

O sketch é **observação**, não esquema: não infere labels ausentes nem
cardinalidade. Ligação com o grafo do sistema é só por caminho de evidência
(sem novo tipo de aresta). Use-o para comparar com o modelo declarado
(`modeling.md`): label no código e fora do design é pergunta; aresta
percorrida sem label aparece como AF-GDB-002, não no sketch.

## Fontes

- Neptune — formato de carga Gremlin CSV: https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-gremlin.html
- Neptune — formatos RDF do loader: https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-rdf.html
- Neptune — comando do loader: https://docs.aws.amazon.com/neptune/latest/userguide/load-api-reference-load.html
- W3C RDF 1.1 N-Triples: https://www.w3.org/TR/n-triples/
- openCypher — funções de conversão: https://neo4j.com/docs/cypher-manual/current/functions/scalar/#functions-tointeger
