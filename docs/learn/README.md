# API Forge — trilha de aprendizado

| Nível | Caminho |
|---|---|
| **Iniciante** | [Quickstart](../installation/quickstart.md) → [first-run](../tutorials/first-run.md) → receita [analisar contrato](recipes/analyze-contract.md) |
| **Intermediário** | [analyze](recipes/analyze-contract.md) → [contract diff](recipes/contract-diff.md) → [case governado](recipes/governed-case.md) → `apiforge doctor` |
| **Avançado** | `apiforge graph`/`evidence`/`brief` → SDD flow (`AGENTS.md`) → evals (`evals agentic-quality`) |
| **Contribuidor** | [sdd-contract](../sdd-contract.md) → `agents/*.md` roster → `apiforge agents lint` antes de commit |
| **Agente (IA)** | [AGENT_PROTOCOL](../../AGENT_PROTOCOL.md) → `apiforge next-step` → saídas `--json` com envelope `{error, exit_code}` |

## Receitas (problema → solução)

### Instalação e hosts

| Tenho este problema | Receita |
|---|---|
| "Primeira vez — instalei e agora?" | [primeiro-uso](recipes/primeiro-uso.md) |
| "Em qual host abro a sessão? Está pronto?" | [integrar-host](recipes/integrar-host.md) |
| "O `.mcp.json` existe mas o host não vê o server" | [verificar-mcp](recipes/verificar-mcp.md) |

### Domínio e contratos

| Tenho este problema | Receita |
|---|---|
| "O código implementa o contrato OpenAPI?" | [analyze-contract](recipes/analyze-contract.md) |
| "O que quebrou entre duas versões da API?" | [contract-diff](recipes/contract-diff.md) |
| "Como evoluir o contrato sem quebrar consumidores?" | [evolucao-api](recipes/evolucao-api.md) |
| "O que esse FastAPI realmente expõe?" | [fastapi](recipes/fastapi.md) |
| "API Java/Go sem OpenAPI — como inventariar?" | [java-go](recipes/java-go.md) |
| "Ler um contrato AsyncAPI em IR" | [asyncapi](recipes/asyncapi.md) |
| "Ler um schema GraphQL SDL em IR" | [graphql](recipes/graphql.md) |
| "Revisar/diff de contrato gRPC" | [grpc](recipes/grpc.md) |

### Modo agentic

| Tenho este problema | Receita |
|---|---|
| "Qual coordenador assume este finding?" | [usar-agents](recipes/usar-agents.md) |
| "Qual skill atende este gatilho?" | [usar-skills](recipes/usar-skills.md) |
| "Quero trabalho governado com evidência" | [governed-case](recipes/governed-case.md) |
| "Conduzir uma mudança pelo SDD" | [sdd](recipes/sdd.md) |
| "O que essa mudança afeta no grafo?" | [graphfy](recipes/graphfy.md) |
| "O que testar antes de declarar pronto?" | [verificacao](recipes/verificacao.md) |
| "Medir economia antes de alegá-la" | [economia](recipes/economia.md) |

Hub do ecossistema (descoberta cross-forge): `the-forge/docs/hub/` — install, which-forge, hosts, MCP, troubleshooting.

Índice gerado: [../INDEX.md](../INDEX.md).
