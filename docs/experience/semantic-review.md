# Revisão semântica — API Forge (FASE 2 §12-equivalente)

Estados: `INVENTORIED` → `AUTOMATICALLY_CHECKED` → `TECHNICALLY_VERIFIED`
→ `SEMANTICALLY_REVIEWED` → `USER_JOURNEY_VALIDATED`. Um estado só sobe
com evidência de leitura/execução real — script verde não promove sozinho.

Revisado em 2026-10 contra o CLI instalado (apiforge dev v0.1.0,
446 comandos inventariados) e um E2E real em projeto FastAPI scratch.

## Correções aplicadas nesta revisão

| Documento | Problema semântico | Correção |
|---|---|---|
| `docs/learn/recipes/analyze-contract.md` | invocava `analyze --project .` com `--out-dir` default — o default `.apiforge` dentro do projeto é **sempre recusado** por `AF-CASE-INPUT-OUTPUT-OVERLAP` (teste em `tests/case/test_service.py` confirma que é design, não bug) | `--out-dir` documentado como obrigatório e fora do projeto; `next-step` com `--findings`/`--phase` reais |
| `docs/learn/recipes/contract-diff.md` | mesma invocação quebrada + case em `.apiforge/case/` | idem; case no `--out-dir` |
| `docs/learn/recipes/governed-case.md` | mesma invocação quebrada | idem |
| `docs/learn/recipes/java-go.md` | sugeria `analyze` sem contrato — `--contract` é obrigatório | reescrito: `discover` (FastAPI) + skill `api-forge-discovery` para Java/Go |
| `docs/learn/recipes/graphfy.md` | `graph query/impact --dir` — flag real é `--graph` | corrigido |
| `docs/HOST_PARITY.md` | sem fluxo de abrir host | seção "Opening a host session" documentando `apiforge ai` |

## Estado por documento

| Documento | Estado | Evidência |
|---|---|---|
| `docs/learn/recipes/primeiro-uso.md` | SEMANTICALLY_REVIEWED | install full + status + ai + verify rodados em scratch real |
| `docs/learn/recipes/integrar-host.md` | SEMANTICALLY_REVIEWED | `apiforge ai`/`ai devin`/`ai devin --launch` rodados; estados observados |
| `docs/learn/recipes/verificar-mcp.md` | SEMANTICALLY_REVIEWED | `install verify` real: BLOCKED sem extra → PASS 153 tools com extra |
| `docs/learn/recipes/analyze-contract.md` | SEMANTICALLY_REVIEWED | `analyze` rodado em FastAPI scratch: 2 findings, case persistido |
| `docs/learn/recipes/contract-diff.md` | AUTOMATICALLY_CHECKED | argv conferido no help; diff de contrato não exercitado em runtime |
| `docs/learn/recipes/governed-case.md` | AUTOMATICALLY_CHECKED | fluxo verify/brief conferido no help |
| `docs/learn/recipes/fastapi.md` | SEMANTICALLY_REVIEWED | `model build` + `analyze` + `next-step` rodados |
| `docs/learn/recipes/java-go.md` | SEMANTICALLY_REVIEWED | `discover --project` rodado: 4 rotas no scratch |
| `docs/learn/recipes/asyncapi.md` | AUTOMATICALLY_CHECKED | `model asyncapi --path` conferido no help |
| `docs/learn/recipes/graphql.md` | AUTOMATICALLY_CHECKED | `model graphql --path` conferido no help |
| `docs/learn/recipes/grpc.md` | AUTOMATICALLY_CHECKED | `grpc discover/analyze/diff` conferidos no help |
| `docs/learn/recipes/evolucao-api.md` | AUTOMATICALLY_CHECKED | `diff contract --baseline/--candidate` conferido |
| `docs/learn/recipes/usar-agents.md` | SEMANTICALLY_REVIEWED | `agents sync/check` + mirrors observados no install real |
| `docs/learn/recipes/usar-skills.md` | AUTOMATICALLY_CHECKED | 14 skills em `.github/skills` confirmadas no disco |
| `docs/learn/recipes/sdd.md` | AUTOMATICALLY_CHECKED | `sdd classify/status/check/stamp` conferidos no help |
| `docs/learn/recipes/graphfy.md` | SEMANTICALLY_REVIEWED | `graph build/query/impact` rodados: 16 nós/14 edges reais |
| `docs/learn/recipes/economia.md` | AUTOMATICALLY_CHECKED | verbos `economy` conferidos no help |
| `docs/learn/recipes/verificacao.md` | AUTOMATICALLY_CHECKED | `verify plan/escalate` conferidos no help |
| `docs/HOST_PARITY.md` | SEMANTICALLY_REVIEWED | comportamento por host observado (devin/claude/codex reais) |
| `docs/installation/*.md` | AUTOMATICALLY_CHECKED | install lifecycle rodado em scratch (install/status/repair/uninstall) |
| `README.md` | AUTOMATICALLY_CHECKED | claims de superfície conferidos contra inventário (446 comandos) |
| `AGENTS.md` | SEMANTICALLY_REVIEWED | contrato de operação + roster conferidos contra `agents/*.md` |

## Pendências declaradas

- TUI §2.3: `apiforge tui <task_id>` é execução por TaskSpec — os
  dashboards de navegação do programa (API Analysis, Contract Explorer,
  Host Manager…) não existem como superfície separada; `experience`
  projeta status/doctor/review. Decisão de escopo pendente.
- Codex em escopo de projeto: o host lê só `~/.codex/config.toml` —
  MCP user-scope via `install --scope user --host codex`.
- 36 links quebrados pré-existentes no índice de docs (não desta onda).
