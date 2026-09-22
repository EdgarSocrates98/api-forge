---
name: api-forge-data-access
description: Analisa e projeta persistência de APIs em Redis/Valkey, MongoDB/DocumentDB, DynamoDB, Neptune e bancos relacionais. Use para access patterns, índices, consistência, transações, TTL, cache, idempotência, queries, hot partitions, traversals, pools e performance de dados.
compatibility: Exige knowledge packs e documentação versionada do provider; nunca captura secrets ou dados de produção sem policy explícita.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Construa `DataAccessIR` com entidade, operação, chave, índice, cardinalidade, consistência, transação, timeout, retry, pool, cache e custo.
2. Extraia access patterns do contrato, código, queries, IaC e traces.
3. Relacione endpoint → serviço → cliente → banco → índice/partição → resultado.
4. Verifique idempotência, concorrência, paginação, N+1, scans, hot keys, hot partitions, lag e backpressure.
5. Separe MongoDB de DocumentDB; valide diferenças de compatibilidade.
6. Para DynamoDB, raciocine por access pattern, PK/SK, GSI/LSI, consistência e throttling.
7. Para Neptune, identifique property graph/RDF, linguagem, labels, cardinalidade e traversals sem limite.
8. Para Redis/Valkey, verifique TTL, eviction, stampede, locks, fencing, streams e invalidação.
9. Proponha índices, schema ou mudanças de acesso apenas com benchmark e rollback.

## Não faça

- não recomende índice sem query ou access pattern;
- não trate eventual consistency como bug automaticamente;
- não confunda cache hit com transação concluída;
- não execute escrita destrutiva em banco;
- não leia valores de secrets, tokens ou documentos sensíveis.

## Entrega

Entregue `DataAccessIR`, facts, findings, access-pattern matrix, riscos de consistência, teste recomendado e evidência necessária.

