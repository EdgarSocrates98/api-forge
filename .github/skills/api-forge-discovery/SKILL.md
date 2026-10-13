---
name: api-forge-discovery
description: >-
  Descobre estaticamente o que uma API expõe — linguagem, framework, rotas,
  handlers, schemas, auth, dependências, bancos, filas, IaC, testes e
  telemetria — e constrói o API-IR com proveniência, sem executar o código
  analisado. Use no início de qualquer revisão, ao receber um repositório
  desconhecido, para inventário, API-IR, mapear contrato ↔ implementação, ou
  quando alguém perguntar "quais endpoints existem", "o que este serviço faz",
  "map this API", "inventory routes". Não use para julgar compatibilidade
  entre versões de contrato (→ api-forge-contract) nem para escolher
  plataforma (→ api-forge-architecture).
compatibility: >-
  Offline; requer o CLI `apiforge`. Extração FastAPI nativa; Spring e Go via
  adapters tree-sitter que nunca executam código nem chamam toolchain. Não
  pressupõe a toolchain da aplicação analisada.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — descoberta e API-IR

Toda conclusão posterior (contrato, segurança, performance) só vale se
apontar para fatos extraídos aqui. Uma descoberta inventada contamina tudo
que vem depois — por isso esta fase extrai e registra, mas não julga.

## Antes de começar

Siga o protocolo de `api-forge-core` (`AGENT_PROTOCOL.md`, caso persistido).
Se o caso já existe, carregue-o e verifique o que mudou com
`apiforge index status` antes de reextrair.

## Procedimento

1. **Inventário determinístico primeiro.** Não abra arquivos arbitrários
   antes de o inventário dizer onde olhar.
   ```text
   apiforge discover --project <dir>                      # FastAPI: rotas sem executar
   apiforge analyze --contract <openapi> --project <dir> --out-dir .apiforge --framework auto
   apiforge index build                                   # TokenSave: 12 índices por hash
   ```
2. **Confirme linguagem e framework.** `--framework auto` conta arquivos; é
   heurística. Reporte o framework detectado e qualquer ambiguidade; repita
   com `--framework spring|go|fastapi` explícito se necessário.
3. **Extraia por superfície** só o que existe no repositório:
   | Superfície | Verbo |
   |---|---|
   | API-IR (contrato + código) | `apiforge model build --contract <c> --project <dir>` |
   | gRPC | `apiforge model proto --path <dir-protos>` |
   | AsyncAPI / GraphQL | `apiforge model asyncapi --path <doc>` · `apiforge model graphql --path <schema>` |
   | IaC | `apiforge model terraform --path <dir-tf>` · `apiforge model sam --path <template>` |
   | Dados e mensageria | `model postgres-access`, `model redis`, `model kafka-access`, `model sqs-access`... (tabelas completas em `api-forge-data-access`, `-messaging`, `-streaming`) |
   | Resiliência | `apiforge model resilience --path <dir>` |
   | Multi-repo | `apiforge workspace discover` · `apiforge workspace graph` (só relações declaradas) |
4. **Proveniência.** Cada fact carrega arquivo, linha/span e hash de entrada.
   Valores dinâmicos (rota montada em runtime, env var, reflexão) viram
   diagnóstico `unresolved`, nunca palpite.
5. **Grafo.** `apiforge graph build --case .apiforge/case --out .apiforge/graph`
   liga operação → handler → dependência; `apiforge graph coverage` aponta
   operações sem implementação e facts sem referência.
6. **Só depois de extrair, compare.** `apiforge judge --contract <c> --project <dir>`
   julga divergência contrato ↔ código; `apiforge next-step` escolhe quem
   continua.

## Guardrails

- Não importe, rode nem faça build da aplicação analisada — a descoberta tem
  de funcionar offline e sem efeitos colaterais.
- Não invente rota, schema, banco, permissão ou fluxo; ausência de evidência
  é `not_observed`, não "não existe".
- Arquivo ausente no repositório não prova ausência no sistema (pode estar em
  outro repo, gerado em build ou injetado por config).
- Heurística de framework nunca vira `confirmed`.
- Não envie o repositório inteiro ao modelo quando um subgrafo ou capsule
  resolver (`api-forge-context`).

## Entrega

- `api-ir`, `facts`, `diagnostics`, `input_hashes` e contagem de `unresolved`;
- framework detectado e grau de confiança;
- divergências contrato ↔ código encontradas por `judge` (se rodado);
- próximo especialista recomendado por `next-step`.

Cada conclusão aponta para `fact_id`. Feche com o Outcome Brief de
`api-forge-core`.
