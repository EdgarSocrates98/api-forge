# Modelagem de grafos — referência

Carregue quando a pergunta for "como modelar" ou quando um finding de
fan-out/supernó exigir mudança de modelo. A extração do API Forge só
**observa** labels e arestas escritos no código (`DomainGraphSketch`); nada
aqui autoriza inferir o modelo real do banco sem dump ou plano.

## Sumário

- Property graph vs RDF
- Vértice, aresta ou propriedade
- Labels, multi-label e ids
- Direção e cardinalidade de arestas
- Supernós e mitigação
- Modelar por access pattern
- Fontes

## Property graph vs RDF

| Eixo | Property graph (Gremlin, openCypher) | RDF (SPARQL) |
|---|---|---|
| Unidade | vértice/nó e aresta com label e propriedades | tripla sujeito–predicado–objeto (quad com named graph) |
| Identidade | id local ao banco (`~id` no Neptune) | IRI global |
| Propriedade em aresta | nativa | reificação, RDF-star ou named graph |
| Esquema | implícito; labels livres | vocabulários/ontologias (RDFS/OWL) |
| Força | traversal operacional, caminhos, recomendações | integração de dados, vocabulário compartilhado, inferência declarada |

No Neptune Database os dois modelos coexistem no cluster mas **não se
enxergam**: dado carregado como property graph não é consultável via SPARQL
e vice-versa. Gremlin e openCypher compartilham o mesmo property graph.
Neptune Analytics trabalha com property graph via openCypher. Neo4j é
property graph (Cypher).

Escolha RDF quando o requisito é interoperabilidade de IRIs/vocabulários;
escolha property graph quando a API faz traversal com filtros em
propriedades de aresta (peso, validade, papel).

## Vértice, aresta ou propriedade

Regras práticas:

- **Vértice** quando a coisa tem identidade própria, é alvo de busca direta
  ou se conecta a mais de uma outra entidade (ex.: `Country`, `Device`).
- **Aresta** quando expressa relação navegável e a API percorre por ela;
  propriedades da relação (desde, papel, peso) ficam na aresta.
- **Propriedade** quando é atributo usado só para filtrar/projetar e nunca
  é ponto de partida de traversal (ex.: `status`, `createdAt`).
- Valor de baixa cardinalidade promovido a vértice (`Gender`, `Status`) cria
  supernó instantâneo — prefira propriedade indexada ou label.
- Evento com tempo (compra, login) costuma ser vértice intermediário
  (`(:User)-[:PLACED]->(:Order)-[:CONTAINS]->(:Product)`), não aresta direta
  com lista de propriedades.

## Labels, multi-label e ids

- Label é o principal filtro barato: toda traversal deve começar por label
  + chave (ver AF-GDB-003, AF-GDB-005).
- Neptune Gremlin aceita multi-label em vértice com separador `::`
  (`addV('Person::Employee')`); openCypher no Neptune e no Neo4j aceita
  `(:Person:Employee)`. Arestas têm um único label/tipo.
- Ids: Neptune permite id definido pelo usuário (`~id` no loader,
  `addV().property(T.id, 'x')` em Gremlin); sem isso gera UUID. Em Neo4j 5
  use `elementId()`; `id()` é interno e pode ser reutilizado após delete —
  nunca exponha como chave de API.
- Prefira chave de negócio estável como id/propriedade única; a API Forge
  não cria constraints, apenas reporta a ausência como pergunta aberta.

## Direção e cardinalidade de arestas

- Modele a direção pelo verbo de domínio (`FOLLOWS`, `OWNS`) e percorra
  na direção natural. Traversal reversa sem label (`in()`, `both()`) é a
  mais cara no Neptune: o explain emite aviso de predicados (AF-GDB-022).
- Declare cardinalidade esperada por tipo de aresta (1:1, 1:N, N:M) no
  design; o código não prova isso — só plano/profile ou estatística.
- Propriedade de vértice no Gremlin do Neptune tem cardinalidade `set` por
  padrão; `property(single, k, v)` substitui. openCypher no Neptune trata
  propriedades como `single`. Misturar as duas APIs no mesmo dado produz
  listas inesperadas.

## Supernós e mitigação

Supernó = vértice com grau muito acima da média (celebridade, `Country:BR`,
tenant raiz). Sintomas: fan-out explosivo, latência caudal, contenção em
escrita concorrente na mesma vizinhança.

| Mitigação | Como | Custo |
|---|---|---|
| Particionar arestas | `FOLLOWS_2026_09` ou vértice-bucket intermediário (`User→Bucket[0..N]→Follower`) | mais saltos; consulta precisa saber o bucket |
| Filtro vertex-centric | filtrar por label **e** propriedade da aresta antes de chegar ao vizinho (`outE('RATED').has('score', gt(4)).inV()`) | depende de o engine usar o filtro cedo |
| Teto de fan-out | `local(outE('X').limit(100))`, `LIMIT` por etapa com `WITH`/`CALL {}` | resultado parcial explícito |
| Desnormalizar contagem | propriedade `followerCount` atualizada em escrita | consistência eventual |
| Mover análise | rodar algoritmo no Neptune Analytics ou em lote | outro serviço/cópia de dados |

Prova de supernó vem de plano executado (razão Units Out/Units In ≥ 1000 →
AF-GDB-025) ou de estatística do banco; nunca do nome do label.

## Modelar por access pattern

1. Liste as perguntas da API (endpoint → traversal) antes do esquema.
2. Para cada uma: ponto de partida (label + chave), arestas percorridas com
   direção, profundidade máxima, filtro e tamanho máximo do resultado.
3. Se a profundidade é aberta, o requisito precisa de teto declarado ou de
   motor analítico — não de traversal online.
4. Compare com o `DomainGraphSketch` extraído: label usado no código e
   ausente do design é pergunta; aresta percorrida sem label é finding.

## Fontes

- Neptune — modelagem e boas práticas: https://docs.aws.amazon.com/neptune/latest/userguide/best-practices.html
- Neptune — multi-label e dados Gremlin: https://docs.aws.amazon.com/neptune/latest/userguide/access-graph-gremlin-differences.html
- Neptune — formato de carga Gremlin (`~id`, `~label`): https://docs.aws.amazon.com/neptune/latest/userguide/bulk-load-tutorial-format-gremlin.html
- TinkerPop reference (cardinalidade, vertex-centric): https://tinkerpop.apache.org/docs/current/reference/
- W3C RDF 1.1 Concepts: https://www.w3.org/TR/rdf11-concepts/
- Neo4j Cypher Manual — `elementId()`: https://neo4j.com/docs/cypher-manual/current/functions/scalar/#functions-elementid
- Neo4j Getting Started — modelagem: https://neo4j.com/docs/getting-started/data-modeling/
