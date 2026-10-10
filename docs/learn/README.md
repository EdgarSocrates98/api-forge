# API Forge — trilha de aprendizado

| Nível | Caminho |
|---|---|
| **Iniciante** | [Quickstart](../installation/quickstart.md) → [first-run](../tutorials/first-run.md) → receita [analisar contrato](recipes/analyze-contract.md) |
| **Intermediário** | [analyze](recipes/analyze-contract.md) → [contract diff](recipes/contract-diff.md) → [case governado](recipes/governed-case.md) → `apiforge doctor` |
| **Avançado** | `apiforge graph`/`evidence`/`brief` → SDD flow (`AGENTS.md`) → evals (`evals agentic-quality`) |
| **Contribuidor** | [sdd-contract](../sdd-contract.md) → `agents/*.md` roster → `apiforge agents lint` antes de commit |
| **Agente (IA)** | [AGENT_PROTOCOL](../../AGENT_PROTOCOL.md) → `apiforge next-step` → saídas `--json` com envelope `{error, exit_code}` |

## Receitas (problema → solução)

| Tenho este problema | Receita |
|---|---|
| "O código implementa o contrato OpenAPI?" | [analyze-contract](recipes/analyze-contract.md) |
| "O que quebrou entre duas versões da API?" | [contract-diff](recipes/contract-diff.md) |
| "Quero trabalho governado com evidência" | [governed-case](recipes/governed-case.md) |

Hub do ecossistema (descoberta cross-forge): `the-forge/docs/hub/` — install, which-forge, hosts, MCP, troubleshooting.

Índice gerado: [../INDEX.md](../INDEX.md).
