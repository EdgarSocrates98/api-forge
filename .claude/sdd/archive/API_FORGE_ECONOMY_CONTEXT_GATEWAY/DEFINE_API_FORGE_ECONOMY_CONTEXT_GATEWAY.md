# DEFINE: API Forge Economy — Context Gateway (P0: Onda 0 + Onda 1)

> Context Gateway nativo que entrega evidência mínima suficiente via `ContextCapsule/v1` + refs `ctx://`, com medição econômica atribuída por fonte e prova de redução sem perda de qualidade.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CONTEXT_GATEWAY |
| **Date** | 2026-09-27 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | `.claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md` |

---

## Problem Statement

Hosts agentic (via MCP) e operadores hostless (via CLI) recebem do API Forge contexto bruto e redundante, e o `economy.jsonl` atual só registra bytes por verbo — sem saber de qual fonte o custo veio nem provar que menos contexto mantém a evidência necessária. Resultado: gasto de contexto não atribuível e nenhuma prova de economia com qualidade.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Agent host (Claude/Codex/Devin) | Consome verbos via MCP | Recebe contexto grande/repetido; precisa ler arquivos inteiros para achar a evidência |
| Operador hostless | Roda `apiforge` via CLI local/CI | Não sabe onde o custo está nem por que um item entrou no contexto |
| Mantenedor do API Forge | Evolui roteamento/contexto | Não consegue provar economia sem regressão de evidência |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1 — `ContextCapsule/v1` e `ContextRef/v1` versionados, registrados em `contracts/registry.py` |
| **MUST** | G2 — Seleção progressiva L0 intent → L1 fingerprint → L2 impact → L3 capsule → L4 focused, guiada por `ContextService` + `GraphImpactAssessment` |
| **MUST** | G3 — Orçamento determinístico (`context_bytes`, `max_level`); estouro → `unresolved` + `AF-CONTEXT-BUDGET-EXHAUSTED`, nunca rebaixamento silencioso |
| **MUST** | G4 — Store content-addressed repo-local `<root>/.apiforge/ctx/<sha256>`; `expand` verifica hash antes de devolver |
| **MUST** | G5 — Serialização canônica (mesmo input → mesmos bytes e mesmo hash) |
| **MUST** | G6 — `RunLedger/v1` + `CostVector/v1` com `source ∈ {graph, contract, code, knowledge, filesystem}`; leitura retrocompatível do `economy.jsonl` legado; `economy report` inalterado |
| **MUST** | G7 — Superfícies CLI + MCP: `context capsule`, `context expand`, `economy stats` |
| **MUST** | G8 — Corpus `evals/corpus/economy/` (12 casos) + `apiforge evals economy` com baseline gravado antes do gateway |
| **MUST** | G9 — Todo refusal com código `AF-*`, `field` e `unlock`, catalogado em `docs/catalog-contract.md` |
| **SHOULD** | G10 — Dedup canônico: schema entra uma vez; DTO/SDK como `parity: true` ou `delta: {missing/extra/changed}` |
| **SHOULD** | G11 — `economy explain <run>` determinístico (regras, sem LLM): por que cada ref entrou (aresta de grafo, target, policy) |
| **COULD** | G12 — `expertise` ids no capsule vindos de `ExpertisePack` já carregados (sem lazy loading) |

---

## Success Criteria

- [ ] SC1 — Baseline de bytes gravado para 12/12 casos antes do gateway ser habilitado no benchmark.
- [ ] SC2 — `evidence_recall` do capsule ≥ recall do baseline em 12/12 casos (quality floor; nenhuma troca de qualidade por bytes).
- [ ] SC3 — Redução mediana de bytes capsule vs baseline ≥ 40% nos 12 casos.
- [ ] SC4 — Serialização canônica: 2 execuções consecutivas do mesmo caso produzem capsule byte-idêntico (100% dos casos).
- [ ] SC5 — Tokens: com `--transcript`, valores observados; sem transcript, 100% das saídas com `observed_tokens: unresolved` (zero estimativas contadas como observadas).
- [ ] SC6 — `economy stats` atribui 100% dos bytes registrados a uma `source` (nenhum bucket "unknown" para emissões do gateway).
- [ ] SC7 — Novos códigos `AF-*` (≥4) presentes no catálogo; teste de catálogo verde.
- [ ] SC8 — Suíte completa + `apiforge sdd check --root docs/sdd` verdes, rodados uma vez ao final do build.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Capsule happy path | fixture `fastapi_orders` com grafo disponível | `apiforge context capsule --target POST:/orders --level L3` | Retorna `ContextCapsule/v1` com refs `ctx://sha256/…` cobrindo schema, handler e testes impactados; `budget.serialized_bytes` preenchido; `unresolved: []` |
| AT-002 | Expand verificado | capsule de AT-001 gravado | `apiforge context expand ctx://sha256/<h>` | Devolve só o objeto; sha256 do conteúdo == `<h>`; entrada `expand` no RunLedger |
| AT-003 | Hash adulterado | objeto em `.apiforge/ctx/<h>` modificado | `context expand ctx://sha256/<h>` | Recusa `AF-CTX-HASH-MISMATCH` com `field` e `unlock`; nada retornado |
| AT-004 | Ref inexistente | store sem `<h>` | `context expand ctx://sha256/<h>` | Recusa `AF-CTX-REF-NOT-FOUND` |
| AT-005 | Orçamento estourado | caso cujo L3 excede `--budget-bytes 2000` | `context capsule … --budget-bytes 2000` | `status: unresolved`, `AF-CONTEXT-BUDGET-EXHAUSTED`, nível atingido reportado; nenhum ref truncado silenciosamente |
| AT-006 | Grafo indisponível | repo sem grafo/workspace | `context capsule --target …` | Capsule degradado explícito (L0/L1) com `AF-CTX-GRAPH-UNAVAILABLE` em `unresolved`; exit code conforme convenção de refusal parcial |
| AT-007 | Canônico | mesmo caso, mesmo SHA | capsule executado 2× | Bytes idênticos e mesmo hash |
| AT-008 | Dedup | schema `OrderRequest` em OpenAPI + DTO | capsule do target | Schema aparece 1× canônico; DTO como `parity: true` ou `delta` |
| AT-009 | Ledger legado | `economy.jsonl` com entradas antigas `{verb, detail_level, payload_bytes}` | `apiforge economy report` e `economy stats` | `report` idêntico ao atual; `stats` lê legado em bucket `legacy` sem erro |
| AT-010 | Tokens unresolved | sem `--transcript` | `economy stats` | `observed_tokens: unresolved`; nenhuma estimativa somada |
| AT-011 | Explain | run com capsule L3 | `economy explain <run>` | Cada ref lista regra de inclusão (`graph-edge:<id>` / `target` / `policy:<id>`) sem chamada LLM |
| AT-012 | Benchmark | corpus 12 casos + baseline gravado | `apiforge evals economy` | Relatório com bytes baseline/capsule, recall por caso, mediana; exit ≠0 se SC2 ou SC3 falharem |
| AT-013 | MCP parity | servidor MCP local | tools `context_capsule`, `context_expand`, `economy_stats`, `economy_explain` | Mesmo payload da CLI; bytes registrados como `mcp:<name>` |

---

## Out of Scope

- Ondas 2–6: CAS compartilhado `~/.apiforge`, parsing/grafo incremental, invalidação por dependência, delta-first (git base/head).
- `BudgetEnvelope/v1` multi-dimensão (calls, fanout, debate rounds, reserva de verificação), `EconomyPlan/v1`, perfis economy/balanced/deep, escalation ladder, stop conditions no router.
- Integração do capsule no runtime/supervisor/`RoutingPlan`/debate.
- Reescrita de host assets (skills/agents) para verb-first.
- Lazy expertise loading, reviewer ROI, shadow budgets, compact MCP separado, log/error slicing, `doctor --economy`, query expansion, verification ladder, test selection, tiering de modelo.
- Extração de `forge-kernel` compartilhado com Spark Forge.
- Qualquer resumo por LLM de contexto.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Sem SDK de provider em `src/`; sem rede; sem mutação live | Gateway 100% determinístico/offline |
| Technical | `economy report` e formato legado de `economy.jsonl` não podem quebrar | Ledger novo coexistente; leitor dual |
| Technical | Contratos como `VersionedContract` no registry; refusals `AF-*` + `field` + `unlock` catalogados | Atualizar `docs/catalog-contract.md` e testes de catálogo |
| Technical | Tokens só observados; estimativa sempre rotulada e separada | Reusa `economy/tokens.py` |
| Process | Edições via `apply_patch`; testes + artefatos SDD (`docs/sdd`) juntos | Build atualiza SDD por onda |
| Process | Testes direcionados por task; suíte completa só uma vez ao final | Plano de build sem suíte por task |
| Process | Novas superfícies CLI/MCP espelhadas nos host mirrors quando aplicável | Checar paridade de hosts |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/context/gateway/`, `src/apiforge/economy/`, `src/apiforge/contracts/context.py`, `src/apiforge/evals/`, `src/apiforge/cli.py` (`context_app`, `economy_app`), `src/apiforge/mcp/tools.py`, `evals/corpus/economy/`, `docs/sdd/API_FORGE_ECONOMY_CONTEXT_GATEWAY/` | Estende módulos existentes; nenhum orquestrador novo |
| **KB Domains** | pydantic, testing, python, genai, prompt-engineering, anti-patterns, component-model | Contratos versionados, testes determinísticos, context engineering sem LLM |
| **IaC Impact** | None | Local-first; só arquivos sob `.apiforge/` |

Reuso confirmado: `ContextService.resolve` (`context/service.py`), `GraphImpactAssessment` (`contracts/graph_impact.py:79`), `ContextResult` (`contracts/context.py:34`), `economy/ledger.py` (`record`, `report`), `economy/tokens.py`, `mcp/tools.py` (`_call` já registra `mcp:<name>`), `economy_app`/`context` Typer em `cli.py`.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | `GraphImpactAssessment` resolve nós direct/transitive para targets nas 8 fixtures | L2 vazio → recall cai; exigiria extração direta por parser OpenAPI/AST como fallback | [ ] |
| A-002 | Contexto atual de `context`/`brief` é baseline justo (inclui evidência obrigatória) | Recall de baseline baixo tornaria SC2 trivial; exigiria baseline "arquivos inteiros do target" | [ ] |
| A-003 | 40% de redução mediana é atingível em fixtures pequenas | Fixtures já compactas → meta ajustada com evidência no BUILD_REPORT, sem baixar SC2 | [ ] |
| A-004 | `required_refs` podem ser expressos por caminho+símbolo estável | Ground truth frágil → usar path+linha âncora por hash de trecho | [ ] |
| A-005 | Store repo-local sem GC não cresce de forma problemática na P0 | Adicionar `context gc` simples (Onda 2 antecipada) | [ ] |
| A-006 | Hash sha256 sobre serialização canônica é estável entre Windows/Linux (line endings) | Normalizar `\n` antes de hash; senão AT-007 falha cross-OS | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Dor, usuários e impacto claros; evidência no código atual |
| Users | 3 | Três personas com dores concretas |
| Goals | 3 | MoSCoW com 12 metas rastreáveis |
| Success | 2 | Métricas numéricas; meta de 40% ainda não validada contra baseline real (A-003) |
| Scope | 3 | Out of scope explícito por onda |
| **Total** | **14/15** | |

---

## Open Questions

- Q1 (Design): exit code para capsule degradado (AT-006) — sucesso parcial (0 + `unresolved`) ou código dedicado? Seguir convenção de refusal parcial existente no CLI.
- Q2 (Design): esquema de ids `ctx://sha256/<hex>` puro vs `ctx://<kind>/<name>@sha256` legível — decidir mantendo hash como identidade.

Nenhuma bloqueia Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-27 | define-agent | Initial version from BRAINSTORM |
| 1.1 | 2026-09-27 | ship-agent | Shipped and archived |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md`
