---
name: api-forge-discovery
description: Descobre APIs, frameworks, rotas, contratos, dependências, bancos, IaC, testes e observabilidade sem executar o código. Use para inventário, API-IR, análise de repositórios, divergência entre contrato e implementação ou preparação de qualquer revisão de API.
compatibility: Requer o repositório API Forge e seus comandos locais; funciona offline e não pressupõe toolchain da aplicação analisada.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Leia `AGENT_PROTOCOL.md` e carregue o caso existente.
2. Execute o inventário determinístico antes de abrir arquivos arbitrários.
3. Detecte linguagem, framework e versão; se houver ambiguidade, reporte-a.
4. Extraia rotas, handlers, schemas, auth, dependências, persistência, filas, cache, IaC e testes.
5. Carregue o contrato OpenAPI/AsyncAPI/GraphQL/protobuf quando existir.
6. Construa ou atualize o API-IR com proveniência, hash e localização.
7. Emita facts sem julgamento e diagnósticos `unresolved` para valores dinâmicos.
8. Compare contrato, código, infraestrutura e evidências existentes somente depois da extração.

## Não faça

- não importe nem execute a aplicação analisada;
- não invente rota, schema, banco, permissão ou fluxo;
- não trate arquivo ausente como inexistente no sistema;
- não transforme heurística de framework em confirmação;
- não envie o repositório inteiro ao modelo quando um subgrafo for suficiente.

## Entrega

Entregue `api-ir`, `facts`, `diagnostics`, `input_hashes`, `unresolved` e o próximo especialista recomendado. Cada conclusão deve apontar para fatos.

