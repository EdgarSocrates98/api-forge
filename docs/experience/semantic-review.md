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
| `src/apiforge/cli.py` | `apiforge --help` **crashava** no console Windows cp1252 — `→` (U+2192) no docstring do `ai` | `->`; gate `test_help_is_cp1252_safe` varre help/params de todos os comandos |
| `src/apiforge/ui/home.py` | menu TUI com `install mcp-verify` (verbo inexistente) e `analyze`/`agents` bare que só imprimem usage | menu reescrito cobrindo os 10 dashboards §2.3 com argv real verificado; gate `test_menu_argv_parse_on_real_cli` parseia cada entrada no app Typer |

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

- TUI §2.3: o menu interativo (`ui/home.py` + `ui/tui.py` full-screen)
  cobre os 10 dashboards exigidos — API Analysis (`status`), Contract
  Explorer (`contract list`), Architecture Explorer (`capabilities
  list`), Agentic Tasks (`forge health`), Test Results (`evals list`),
  Verification (`verify plan`), Evidence (`field report`), History
  (`runtime telemetry-query`), Installation (`install status`), Host
  Manager (`ai`) — cada entrada é argv real que o teste de contrato
  parseia no app Typer. `apiforge tui <task_id>` continua sendo a
  projeção de execução por TaskSpec (superfície separada, não
  substituída).
- Codex em escopo de projeto: o host lê só `~/.codex/config.toml` —
  MCP user-scope via `install --scope user --host codex`.
- 36 links quebrados pré-existentes no índice de docs (não desta onda).
