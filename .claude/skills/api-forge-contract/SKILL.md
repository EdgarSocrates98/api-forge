---
name: api-forge-contract
description: >-
  Projeta, revisa e evolui contratos de API — OpenAPI, AsyncAPI, GraphQL,
  protobuf/gRPC, HTTP semantics e Problem Details — e classifica mudanças
  entre versões como breaking, risky, compatible ou unresolved. Use para
  design-first, revisão de spec, breaking change, versionamento, deprecação,
  idempotência, paginação, modelo de erro, compatibilidade de consumidores,
  gRPC-Gateway ou documentação viva; também quando alguém perguntar "isto
  quebra clientes?", "is this a breaking change", "review my openapi", "diff
  these specs". Não use para inventariar uma API sem contrato (→
  api-forge-discovery) nem para testar o contrato em runtime (→
  api-forge-verification).
compatibility: >-
  Offline; requer o CLI `apiforge`. Spectral, Redocly, oasdiff, Schemathesis,
  Pact, protoc e Buf são adapters opcionais — sem eles, registre a limitação
  em vez de presumir o resultado.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — contratos e compatibilidade

O contrato é a promessa feita a quem você não vê. Esta skill trata cada
mudança como potencialmente quebrando um consumidor desconhecido até que a
evidência diga o contrário.

## Antes de começar

Siga `api-forge-core`. Identifique: contrato baseline, candidato, protocolo
(`openapi` ou `grpc`), consumidores conhecidos e política de
compatibilidade declarada (semver, data de deprecação, janela de suporte).

## Procedimento

1. **Valide sintaxe e semântica.** Sintaxe válida não prova bom design.
2. **Revise o design por operação:** recursos e nomes, métodos e status,
   headers, schemas e composição (`oneOf`/`allOf`), exemplos, paginação,
   filtros, erros (`application/problem+json`), segurança por operação,
   idempotência (`Idempotency-Key` em POST com efeito), retryability, limites
   de payload e rate limit. Consulte as regras com `apiforge rules list
   --area contract` e `apiforge rules lookup <id>`.
3. **Classifique a evolução** entre baseline e candidato:
   ```text
   apiforge diff contract --baseline <old.yaml> --candidate <new.yaml>
   apiforge contract-intel impact --protocol openapi|grpc --baseline <old> --candidate <new>
   apiforge grpc diff <old-dir> <new-dir>                # regras de evolução protobuf
   ```
   Classes: `breaking`, `risky`, `compatible`, `unresolved`.
4. **Ligue cada finding** a regra, operação e consumidor afetado. Sem
   evidência de consumidor, o impacto é `unresolved`, não "nenhum".
5. **Contrato ↔ código.** `apiforge judge --contract <c> --project <dir>`
   mostra rotas do contrato sem implementação e vice-versa.
6. **gRPC** quando aplicável: `apiforge grpc analyze`, `grpc verify`,
   `grpc gateway` (projeção REST) e `grpc codegen` (relata toolchain ausente
   em vez de falhar em silêncio).
7. **Simule antes de publicar** mudanças arriscadas:
   `apiforge contract-intel twin` cria um Digital Twin sem rede.
8. **Proponha a correção como contrato/diff.** Não altere código sem TaskSpec
   e sandbox.

## Regras de honestidade

- Operação sem evidência de consumidor não prova ausência de consumidores.
- Mudança compatível no schema pode quebrar um consumidor específico
  (ex. enum novo em cliente com switch exaustivo; campo antes opcional que o
  cliente nunca enviou).
- `202 Accepted` exige modelo de status: polling, callback ou evento.
- Erro estruturado nunca expõe stack trace, SQL ou segredo.
- Remover campo, endurecer validação, mudar tipo, renomear e mudar default
  são breaking até prova contrária.
- Em protobuf, reusar número de campo ou mudar tipo de wire é sempre
  breaking; reserve números removidos.

## Entrega

- contrato candidato ou diff proposto;
- classificação por mudança (`breaking|risky|compatible|unresolved`) com
  regra e operação;
- consumidores afetados (ou gap explícito);
- decisão de versionamento e plano de deprecação;
- testes de contrato recomendados (Schemathesis, Pact) — execução fica com
  `api-forge-verification`.

Especialistas típicos: `api-contract-architect` (design novo),
`api-governance-reviewer` (evolução de contrato publicado),
`api-codegen-engineer` (stubs e gateway), `api-dx-docs-reviewer` (docs e SDKs).
