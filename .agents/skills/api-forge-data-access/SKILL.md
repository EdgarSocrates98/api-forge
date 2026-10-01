---
name: api-forge-data-access
description: >-
  Analisa e projeta como uma API usa seus bancos — PostgreSQL, MySQL,
  RDS/Aurora, Redis/Valkey/ElastiCache, MongoDB/DocumentDB, DynamoDB,
  OpenSearch e Redshift — produzindo DataAccessIR, access patterns, índices,
  consistência, transações, TTL/cache, idempotência, pools, paginação, N+1,
  scans, hot keys e hot partitions. Use quando a pergunta for "o que este
  código faz com o banco", query lenta, índice, modelagem de chave (PK/SK,
  GSI), cache stampede, lock distribuído, pool esgotado ou revisão de
  persistência. Não use para graph stores — Neptune, Neo4j, Gremlin,
  openCypher, SPARQL (→ api-forge-graph), para filas/eventos (→
  api-forge-messaging ou api-forge-streaming), para provar throughput sob carga (→
  api-forge-performance) nem para timeouts/retries como resiliência (→
  api-forge-verification).
compatibility: >-
  Offline; requer o CLI `apiforge`. Análise estática por `model *-access`;
  postura AWS via `apiforge collect` (opt-in, read-only). Nunca lê secrets,
  valores de documentos ou dados de produção sem policy explícita.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — acesso a dados

A maior parte dos incidentes de API acaba no banco: scan sem limite, chave
quente, pool esgotado, transação longa. Esta skill liga cada endpoint ao que
ele faz no store, para que recomendações nasçam de access patterns reais e
não de boas práticas genéricas.

## Antes de começar

Siga `api-forge-core`. Identifique os stores pelo inventário
(`api-forge-discovery`) e confirme a versão/engine declarada — MongoDB e
DocumentDB, PostgreSQL e Aurora PostgreSQL não são intercambiáveis.

## Extração por store

| Store | Código | Postura AWS (dump offline) |
|---|---|---|
| PostgreSQL / MySQL / Aurora (visão geral) | `apiforge model rds-access --path <dir>` | `collect rds --resource-id <id>` (dump guardado como evidência; sem reader `model` dedicado — gap) |
| PostgreSQL | `apiforge model postgres-access --path <dir>` | idem |
| MySQL | `apiforge model mysql-access --path <dir>` | idem |
| Redis / Valkey | `apiforge model redis --path <dir>` | `collect elasticache --replication-group-id <id>` → `model elasticache --path <dump>` |
| ElastiCache (código) | `apiforge model elasticache-access --path <dir>` | idem |
| MongoDB / DocumentDB | `apiforge model mongo --path <dir>` | `collect docdb --cluster-id <id>` → `model docdb --path <dump>` |
| DynamoDB | `apiforge model dynamodb-access --path <dir>` | `collect dynamodb --table-name <t>` → `model dynamodb --path <dump>` |
| OpenSearch | `apiforge model opensearch-access --path <dir>` | — |
| Redshift | `apiforge model redshift-access --path <dir>` | — |

Graph stores (Neptune Database/Analytics, Neo4j; Gremlin, openCypher,
SPARQL) não ficam aqui: use `api-forge-graph` (especialista
`api-graph-data-architect`).

Todo `collect` é opt-in, read-only, usa credencial do host e aceita
`--out <dump-dir> --now <ISO>`; pergunte antes com
`apiforge evidence gate --question "..."`.

Depois: `apiforge judge --facts <facts.json>` aplica o catálogo; detalhe de
cada regra com `apiforge rules lookup <id>`.

## Procedimento

1. **Monte o `DataAccessIR`:** entidade, operação, chave, índice,
   cardinalidade, consistência, transação, timeout, retry, pool, cache e
   custo — cada campo com `fact_id` ou marcado `unresolved`.
2. **Extraia access patterns** do contrato, código, queries, IaC e traces.
3. **Relacione** endpoint → serviço → cliente → store → índice/partição →
   resultado (`apiforge graph trace` ajuda a provar o caminho).
4. **Verifique riscos transversais:** idempotência de escrita, concorrência
   (lost update, optimistic lock), paginação estável (cursor vs offset), N+1,
   scans sem limite, hot keys, hot partitions, lag de réplica, backpressure.
5. **Por store:**
   - **Relacional:** plano de query só com `EXPLAIN` fornecido; isolamento,
     duração de transação, pool vs `max_connections`, migrations reversíveis.
   - **DynamoDB:** raciocine por access pattern → PK/SK, GSI/LSI, consistência
     de leitura, throttling, item size, `Scan` como finding.
   - **MongoDB/DocumentDB:** índices compostos, `$lookup`, operadores não
     suportados no DocumentDB, read/write concern.
   - **Redis/Valkey:** TTL, eviction policy, stampede, locks com fencing token,
     streams, invalidação, cache hit ≠ escrita concluída.
   - **OpenSearch/Redshift:** mapping/shards, queries sem filtro, carga
     analítica em caminho síncrono de API.
6. **Proponha mudança** (índice, schema, padrão de acesso) só com benchmark
   antes/depois e rollback; a medição fica com `api-forge-performance`.

## Guardrails

- Não recomende índice sem a query ou access pattern que o usa — índice tem
  custo de escrita e storage.
- Não trate eventual consistency como bug automaticamente; verifique o
  requisito do endpoint.
- Não execute escrita, DDL ou comando destrutivo em banco; o core é
  read-only.
- Não leia valores de secrets, tokens, connection strings ou documentos
  sensíveis — referencie o nome do recurso, não o conteúdo.
- Análise estática não prova latência, lag ou throughput; declare como gap.

## Entrega

`DataAccessIR`, facts, findings com regra, matriz de access patterns
(endpoint × store × operação × chave/índice), riscos de consistência, teste
recomendado e evidência necessária para fechar cada `unresolved`.

Especialista típico: `api-data-access-architect`.
