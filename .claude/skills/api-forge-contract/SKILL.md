---
name: api-forge-contract
description: Projeta, revisa e evolui contratos de APIs com OpenAPI, AsyncAPI, GraphQL, protobuf, HTTP e Problem Details. Use para design-first, breaking changes, versionamento, idempotência, paginação, erros, compatibilidade e documentação viva.
compatibility: Pode usar ferramentas locais como Spectral, Redocly, oasdiff, Schemathesis ou Pact quando disponíveis; sem elas, registre a limitação.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Identifique contrato, consumidores, versão e política de compatibilidade.
2. Valide sintaxe e semântica; sintaxe válida não prova bom design.
3. Verifique recursos, métodos, status, headers, erros, schemas, exemplos, paginação e filtros.
4. Verifique segurança por operação, idempotência, retryability, limites de payload e rate limits.
5. Compare baseline e candidato; classifique mudanças breaking, risky, compatible ou unresolved.
6. Relacione cada finding a regra, operação e consumidor afetado.
7. Proponha correções como contrato/diff; não altere código sem task e sandbox.

## Regras de honestidade

- uma operação sem consumer evidence não prova ausência de consumidores;
- uma mudança compatível para um schema pode ser breaking para um consumidor específico;
- `202 Accepted` exige modelo de status, polling, callback ou evento;
- erro deve ser estruturado e não deve expor stack trace ou segredo;
- desconhecimento de consumidores é um gap explícito.

## Entrega

Produza contrato candidato, diff, classificação, impacto, unresolved, testes de contrato e decisão de versionamento.

