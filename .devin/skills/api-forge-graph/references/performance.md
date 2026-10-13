# Desempenho de traversal — referência

Carregue quando a pergunta for "isso escala?" ou quando houver finding de
fan-out, path aberto ou algoritmo do Neptune Analytics. Análise estática
mostra a **forma** da traversal; latência e throughput reais exigem plano
executado e medição (`api-forge-performance`, especialista
`api-performance-engineer`).

## Sumário

- Orçamento de fan-out
- Matemática da explosão de caminhos
- Paginação e batching
- Supernós em runtime
- Cache e réplicas
- Neptune Analytics (AF-GDB-009, AF-GDB-010)
- Quando mover para Analytics
- Fontes

## Orçamento de fan-out

Declare por endpoint, antes de otimizar:

| Item | Exemplo |
|---|---|
| Ponto de partida | 1 vértice (`User` por `userId`) |
| Saltos máximos | 2 |
| Fan-out máximo por salto | 200 (`local(out('FOLLOWS').limit(200))`) |
| Resultado máximo | 50 |
| Teto de traversers | 1 × 200 × 200 = 40 000 |

Se o teto de traversers não cabe no orçamento de latência do endpoint, o
requisito precisa mudar (menos saltos, filtro mais seletivo, pré-cálculo),
não o índice.

## Matemática da explosão de caminhos

Com grau médio *b* e profundidade *d*:

- caminhos/traversers ≈ *b^d* sem `dedup()`;
- vértices distintos ≤ min(*b^d*, |V|), mas o trabalho é proporcional aos
  caminhos até o ponto do `dedup()`;
- grau com cauda pesada (lei de potência) torna a média enganosa: um único
  supernó no primeiro salto domina o total.

| *b* | *d* = 2 | *d* = 3 | *d* = 4 |
|---|---|---|---|
| 10 | 100 | 1 000 | 10 000 |
| 50 | 2 500 | 125 000 | 6 250 000 |
| 200 | 40 000 | 8 000 000 | 1,6 × 10⁹ |

Por isso AF-GDB-001 (repeat sem parada), AF-GDB-004 (path aberto) e
AF-GDB-007 (property path ilimitado) são altas mesmo com `LIMIT` no final:
o limite final não poda o frontier intermediário.

## Paginação e batching

- Offset alto (`range(10000, 10050)`, `SKIP 10000`) refaz o prefixo a cada
  página; use cursor por chave ordenável.
- Busque N vizinhos de M vértices numa traversal só
  (`g.V(ids).out('X')...`, `UNWIND $ids AS id MATCH ...`) em vez de M
  chamadas (N+1 de grafo). Limite o tamanho do lote: lote grande é uma
  query longa que segura recursos.
- Escritas em lote: agrupe por transação com tamanho limitado; no Neptune
  carga massiva é trabalho do bulk loader (`neptune.md`), não de API.

## Supernós em runtime

- Filtre arestas pelo label **e** por propriedade antes de chegar ao
  vizinho; limite por elemento com `local(...limit(n))` ou
  `WITH ... LIMIT n` intermediário.
- Escrita concorrente na vizinhança de um supernó gera conflito de
  transação (no Neptune, `ConcurrentModificationException`): o retry é
  política de `api-resilience-engineer`; a causa é de modelo.
- Plano executado com razão ≥ 1000 (AF-GDB-025) é o sinal objetivo.

## Cache e réplicas

- Resultado de traversal estável (recomendação diária, árvore de
  categorias) cabe em cache de aplicação com TTL; invalidação por evento
  (Neptune Streams) quando a frescura importa.
- No Neptune, leituras analíticas e relatórios vão ao **reader endpoint**;
  o writer fica para a API transacional. Réplicas têm lag (métrica
  `ClusterReplicaLag`): leitura-após-escrita exige o writer.
- Cache de plano/compilação depende de texto estável: parâmetros em vez de
  concatenação (AF-GDB-008).

## Neptune Analytics (AF-GDB-009, AF-GDB-010)

Neptune Analytics é um grafo em memória consultado por openCypher, com
algoritmos via `CALL neptune.algo.<nome>(...)` e busca vetorial via
`CALL neptune.algo.vectors.*`.

- **AF-GDB-009** — `CALL neptune.algo.*` sem `MATCH` anterior que escope os
  nós de entrada roda o algoritmo sobre o grafo inteiro. Escope:

  ```cypher
  MATCH (n:Airport {code: $code})
  CALL neptune.algo.bfs(n, {maxDepth: 3})
  YIELD node RETURN node LIMIT 100
  ```

- **AF-GDB-010** — `CALL neptune.algo.vectors.*` sem `topK` devolve
  vizinhos sem teto declarado. Declare:

  ```cypher
  CALL neptune.algo.vectors.topKByEmbedding($embedding, {topK: 10})
  YIELD node, score RETURN node, score
  ```

Nomes e parâmetros exatos de cada algoritmo variam; confira a página do
algoritmo antes de recomendar.

## Quando mover para Analytics

Considere Neptune Analytics (ou processamento em lote) quando:

- a pergunta percorre o grafo inteiro (centralidade, comunidades,
  PageRank, componentes conectados, caminho mínimo em grafo grande);
- o endpoint pede profundidade aberta que não cabe no orçamento de fan-out;
- há busca vetorial combinada com vizinhança.

Custos: cópia/sincronização dos dados, capacidade em memória provisionada,
frescura limitada pela carga. Decisão de plataforma é de
`api-platform-selector`; topologia de `api-architecture-reviewer`.

## Fontes

- Neptune — boas práticas Gremlin: https://docs.aws.amazon.com/neptune/latest/userguide/best-practices-gremlin.html
- Neptune — boas práticas openCypher: https://docs.aws.amazon.com/neptune/latest/userguide/best-practices-opencypher.html
- Neptune — erros e retry de transação: https://docs.aws.amazon.com/neptune/latest/userguide/transactions-exceptions.html
- Neptune Analytics — algoritmos: https://docs.aws.amazon.com/neptune-analytics/latest/userguide/algorithms.html
- Neptune Analytics — busca vetorial: https://docs.aws.amazon.com/neptune-analytics/latest/userguide/vector-index.html
- TinkerPop — local step: https://tinkerpop.apache.org/docs/current/reference/#local-step
