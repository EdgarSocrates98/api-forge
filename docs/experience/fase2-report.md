# FASE 2 — API Forge como plataforma agentic de referência

Relatório de fechamento da FASE 2 do `prompt_evo_foco1.md`. Cada item cita
a evidência que o sustenta; nada aqui é promovido por conveniência.

## §2.1 — Padronização (contratos FASE 0)

| Requisito | Estado | Evidência |
|---|---|---|
| Ciclo de vida de install | FEITO | `install --scope project|workspace|user --host {claude,devin,codex,copilot,all}` rodado em scratch real (`af-host-check`): recibo `forge/InstallReceipt/v1`, `completed`, verification PASS, `.mcp.json` gerenciado, mirrors em `.devin`/`.claude`/`.agents`/`.github`. `status`/`doctor`/`repair`/`uninstall` exercitados; drift em config gerenciado degrada e `repair` restaura. |
| Recibo honesto | FEITO | Install `--host codex` em escopo projeto emite `mcp-scope:codex NOT_APPLICABLE` (Codex 0.160.0 não lê `.mcp.json` de projeto — verificado nativamente). Vindo do installkit canônico re-vendored (sha `0eae54fd`). |
| Superfícies | FEITO | CLI 446 comandos inventariados; MCP `tools/list` = 154 tools incluindo `ai_observe`; `graph view` emite `forge/ForgeGraphView/v1`. |

## §2.2 — Agent-First

| Item | Estado | Evidência |
|---|---|---|
| Devin | FEITO | Host-nativo: `devin mcp list` no scratch lista `apiforge` (cmd `apiforge-mcp`); 14 skills descobertas pelo harness; `ai devin` → `READY` (drift_ok=50, mcp present). |
| Claude | FEITO | `ai claude` → `READY`; mirrors `.claude/` aterrissados no install. |
| Codex | FEITO | `ai codex` → `READY`; limitação de MCP projeto-escopo declarada no recibo (`NOT_APPLICABLE`), caminho real via `--scope user` documentado. |
| MCP | FEITO | Handshake real initialize→initialized→tools/list: 154 tools; `ai_observe` dispatchado via `apiforge_call` retorna estado observado (`launched: false` sempre — launch é fronteira humana CLI-only). |
| Skills | FEITO | 15 skills no catálogo regenerado; mirrors verificados em disco no install. |
| Agents | FEITO | 32 agents no catálogo (27 coordenadores + 5 executors); `.agents/agents/` aterrissa no install (subagent profiles nativos do Devin). |
| Task routing | FEITO | `next-step` no E2E real roteou `api-governance-reviewer` a partir dos findings. |
| Execution | FEITO | Pipeline E2E real (abaixo) + TUI por TaskSpec (`apiforge tui <id>`). |
| Verification | FEITO | `verify plan` no case real → ladder V5 com escalada honesta ("no-impacted-tests-found"); `verify escalate` → `stop` com razão declarada. |
| Abrir host | FEITO | `apiforge ai`/`ai <host>`/`ai <host> --launch` — launch real verificado (Devin REPL abriu; recusas nomeadas: `host_missing`, `login_required`, `no_tty`, `all`). |

## §2.3 — TUI

- Menu cobre os 10 dashboards exigidos com argv real: API Analysis
  (`status`), Contract Explorer (`contract list`), Architecture Explorer
  (`capabilities list`), Agentic Tasks (`forge health`), Test Results
  (`evals list`), Verification (`verify plan`), Evidence (`field report`),
  History (`runtime telemetry-query`), Installation (`install status`),
  Host Manager (`ai`).
- Contrato endurecido: `test_menu_argv_parse_on_real_cli` parseia cada
  entrada no app Typer — pegou `install mcp-verify` (verbo inexistente)
  e `judge`/`analyze`/`agents` bare que só imprimiam usage.
- Fallback não-TTY honesto: `apiforge` bare sem TTY imprime o sumário de
  produto; `run_home` só abre com stdin+stdout TTY.
- Bug real corrigido: `apiforge --help` crashava no cp1252 do Windows
  (`→` no docstring do `ai`); gate `test_help_is_cp1252_safe` varre
  help/params de todos os comandos.

## §2.4 — Graph

`graph build` no case E2E → 13 nós/10 edges reais; `graph query` e
`graph impact` funcionais; `graph view` emite `forge/ForgeGraphView/v1`;
`graph ui --no-browser` serve o Graph Studio local (HTTP 200 verificado).

## §2.5 — Documentação PT-BR

18 receitas em `docs/learn/recipes/` cobrindo o conjunto exigido:
primeiro uso, FastAPI, OpenAPI/contratos, AsyncAPI, GraphQL, gRPC,
Java/Go, breaking changes, evolução, agents, skills, MCP, host
integration, Graphfy, SDD, economia, verificação — escritas com comandos
executados de verdade antes de documentar.

Revisão semântica real (`docs/experience/semantic-review.md`) corrigiu
contradições: `--out-dir` obrigatório fora do projeto (o default
`.apiforge` colide com `--project .` por design,
`AF-CASE-INPUT-OUTPUT-OVERLAP`), `--graph` vs `--dir` inventado,
`discover` FastAPI-only vs claim Java/Go. `HOST_PARITY.md` em
USER_JOURNEY_VALIDATED; PT-BR espelhado.

## §2.6 — E2E real

FastAPI scratch: `discover` (4 rotas) → `model build` (contrato) →
`analyze` com drift real (rota fora do contrato + mudança de tipo) →
2 findings → `next-step` roteia `api-governance-reviewer` → `graph build`
→ `evidence`/`brief`. Integração de host verificada em scratch separado
(install → `devin mcp list` → `ai` READY).

## Gates executados nesta fase

| Gate | Resultado |
|---|---|
| `install lifecycle` | 17 verdes (scratch real completo) |
| `mcp_protocol` + `trust` | 22 + 73 verdes (ai_observe na allowlist, perfil de risco) |
| Docs drift (`check_docs`) | 1200 arquivos, 0 problemas |
| Catálogos (`doc_catalogs`) | regenerados; folded `>-` parseado; fallback lê corpo pós-frontmatter |
| TUI/cli/hosts | 8 + 12 verdes (menu argv + cp1252 + ai flow) |
| Suíte integral | **1856 passed, 1 skipped** em 4m09s — `pytest tests -q` no HEAD da fase |

## Limitações declaradas (não escondidas)

- Copilot: binário não instalado nesta máquina — `ai` reporta
  `NOT_DETECTED`; claims não promovidos.
- Codex projeto-escopo: MCP não é consumível (host só lê
  `~/.codex/config.toml`); declarado `NOT_APPLICABLE` no recibo.
- `contract-diff`/`perf`/adapters live: argv conferido, não exercitado
  em runtime real nesta onda (AUTOMATICALLY_CHECKED no ledger).
- 36 links quebrados pré-existentes no índice de docs (não desta onda).
