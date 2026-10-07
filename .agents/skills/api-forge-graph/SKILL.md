---
name: api-forge-graph
description: >-
  Analisa e projeta como uma API usa bancos de grafo — Amazon Neptune
  (Database e Analytics) e Neo4j — em Gremlin, openCypher e SPARQL,
  produzindo GraphAccessIR, DomainGraphSketch, GraphPlanIR (explain/profile),
  findings AF-DATA-013 e AF-GDB-*, e exportando o grafo do sistema para
  Neptune (CSV do bulk loader) ou RDF. Use quando a pergunta for traversal
  sem limite, repeat sem parada, fan-out sem label, supernó, property graph
  vs RDF, leitura de plano, algoritmo do Neptune Analytics, busca vetorial
  ou carga do grafo do sistema num graph store. Não use para bancos
  relacionais, documento, chave-valor, busca ou analíticos (→
  api-forge-data-access), para IAM/VPC/Terraform do cluster (→
  api-forge-architecture), para alarmes CloudWatch (→
  api-forge-observability) nem para provar latência sob carga (→
  api-forge-performance).
compatibility: >-
  Offline; requer o CLI `apiforge`. Extração estática por `model
  graph-access`; planos importados de dumps. O único acesso de rede é o
  collector opt-in `collect neptune-explain` (allowlist read-only, explain
  que não executa por padrão). Nunca muta grafo, cria índice ou lê dados.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — bancos de grafo (Neptune, Neo4j)

Traversal de grafo falha de forma combinatória: um `repeat()` sem parada ou
um `out()` sem label num supernó lê milhões de arestas para devolver dez
linhas. Esta skill liga cada call site ao formato da traversal e, quando há
plano importado, à cardinalidade observada — e declara `unresolved` quando
não há.

## Antes de começar

Siga `api-forge-core`. Confirme o vendor e o modelo: Neptune Database
(Gremlin, openCypher, SPARQL), Neptune Analytics (openCypher + algoritmos)
ou Neo4j (Cypher). Property graph e RDF não são intercambiáveis.

## Fluxo de comandos

```text
apiforge model graph-access --path <dir>          # vendor detectado
apiforge model neptune-access --path <dir>        # força Neptune
apiforge model neo4j-access --path <dir>          # força Neo4j
apiforge rules list --area GDB
apiforge judge --facts <facts.json>
apiforge model graph-explain --path <dump> [--format <fmt>] [--synthetic]
apiforge collect neptune-explain --endpoint <url> --language gremlin|opencypher \
  --query <texto> --out <dump-dir> [--profile --reader-endpoint <url>]
apiforge collect neptune --cluster-id <id>  →  apiforge model neptune --path <dump>
apiforge graph export --format neptune|rdf
```

1. **Extraia** call sites (fact `data.graph.query`) e leia o
   `GraphAccessIR`: vendor, linguagem, `bounded`, `mutation`, labels,
   `shape_risks`, `query_dynamic`, mais o `DomainGraphSketch`.
2. **Julgue** AF-DATA-013 e AF-GDB-001..010 (estáticas); cite `fact_id`.
3. **Planos:** importe dumps com `model graph-explain` → `GraphPlanIR` →
   AF-GDB-020..025. Call site sem plano mantém cardinalidade `unresolved`.
4. **Collector (opt-in):** pergunte antes com
   `apiforge evidence gate --question "..."`. Padrão = explain que não
   executa; `--profile` executa a query e exige `--reader-endpoint` igual a
   `--endpoint` e texto estático sem mutação.
5. **Postura do cluster:** `collect neptune` → `model neptune`.
6. **Grafo do sistema:** `graph export --format neptune|rdf` para bulk load.

## Regras

| Código | Sinal |
|---|---|
| AF-DATA-013 | traversal/query sem limite |
| AF-GDB-001 / 002 / 003 | `repeat()` sem parada / fan-out sem edge label / início sem filtro |
| AF-GDB-004 / 005 / 006 | path de tamanho variável aberto / nó sem label / padrão cartesiano |
| AF-GDB-007 / 008 | property path SPARQL ilimitado / texto de query dinâmico |
| AF-GDB-009 / 010 | algoritmo Analytics sem escopo / busca vetorial sem `topK` |
| AF-GDB-020..025 | plano: step não nativo, estimativa ilimitada, aviso de predicados, scan de todos os labels, AllNodesScan/CartesianProduct, fan-out ≥ 1000 |

## Recusas e diagnósticos

| Código | Quando | Desbloqueio |
|---|---|---|
| AF-GDB-COLLECT-OP | operação fora da allowlist | usar explain/profile permitidos |
| AF-GDB-COLLECT-ARG | argumento inválido/ausente | corrigir o campo indicado |
| AF-GDB-EXPLAIN-SPARQL | SPARQL via collector | rodar explain e importar o dump |
| AF-GDB-PROFILE-MUTATION | query muta o grafo | enviar query read-only |
| AF-GDB-PROFILE-READER | `--profile` sem reader declarado | `--reader-endpoint` = `--endpoint` |
| AF-GDB-PROFILE-DYNAMIC | `--profile` com texto dinâmico | fornecer texto estático |
| AF-GDB-PLAN-FORMAT | formato de plano desconhecido | passar `--format` |
| AF-GDB-PLAN-PARSE | plano ilegível | corrigir/recapturar o dump |

Diagnósticos: `AF-GDB-PARSE` (arquivo não parseável), `AF-GDB-HEURISTIC`
(Java/Go/TS por regex), `AF-GDB-DYNAMIC-QUERY` (texto montado em runtime).
Toda recusa preserva `code`, `field` e `unlock`. `AF-GRAPH-*` pertence ao
grafo do sistema (build/export), não a bancos de grafo.

## Referências

Carregue só a que a pergunta exige:

- `references/modeling.md` — property graph vs RDF, vértice/aresta/propriedade, supernós.
- `references/gremlin.md` — padrões e anti-padrões ↔ AF-GDB-001/002/003/008, AF-DATA-013.
- `references/opencypher.md` — AF-GDB-004/005/006, dialetos Neptune vs Neo4j.
- `references/sparql.md` — AF-GDB-007, LIMIT, updates, named graphs.
- `references/plans.md` — leitura de explain/profile por formato ↔ AF-GDB-020..025.
- `references/performance.md` — fan-out, explosão de caminhos, AF-GDB-009/010.
- `references/neptune.md` — Database vs Analytics, IAM/SigV4, loader, Streams, allowlist.
- `references/neo4j.md` — drivers, dialeto, índices, EXPLAIN/PROFILE.
- `references/system-graph-bridge.md` — `graph export` e DomainGraphSketch.

## Guardrails

- Não execute query fora do collector guardado; nunca mute grafo nem crie
  índice/constraint.
- Não infira cardinalidade, label ou supernó sem plano ou dump; declare gap.
- Fixture sintética (`--synthetic`) nunca é evidência de campo.
- Redija literais de query antes de commitar dumps reais.

## Fronteiras

IAM, VPC e Terraform → `api-infra-reviewer`; topologia AWS →
`api-architecture-reviewer`; monitores CloudWatch/vendor →
`api-observability-integration-engineer`; timeouts/retries →
`api-resilience-engineer`; exploração de injeção → `api-security-reviewer`;
baseline de latência → `api-performance-engineer`.

## Entrega

`GraphAccessIR`, `GraphPlanIR`, findings com regra e `fact_id`, matriz
label × padrão de acesso, lacunas `unresolved` e o plano necessário para
fechar cada uma.

Especialista típico: `api-graph-data-architect`.
