# BRAINSTORM: API Forge Economy — Context Gateway (programa 6 ondas, fatia P0)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_CONTEXT_GATEWAY |
| **Date** | 2026-09-27 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** `prompt_evo_economy.md` (4355 linhas, 118 seções) — levar a filosofia de economia do Spark Forge (PRs #104/#106/#107: Context Gateway, `ctx://`, perfis economy/balanced/deep, benchmark econômico, tokens só observados) para o API Forge como arquitetura econômica nativa, não cópia de código. Princípio: *minimizar contexto, computação e raciocínio agentic necessários para um resultado suficientemente comprovado — nunca minimizar para produzir resultado apenas barato.*

**Context Gathered:**
- `src/apiforge/economy/ledger.py` já grava `{verb, detail_level, payload_bytes}` em `.apiforge/economy.jsonl`; best-effort, nunca quebra a chamada.
- `src/apiforge/economy/tokens.py` já separa tokens observados (transcript) de estimativa rotulada (`--estimate`); custo só com `--cost-basis`.
- `src/apiforge/context/service.py` (`ContextService`) combina `ContextScope/v1` (repo/workspace/target; direct/transitive/all) + `measure_funnel`.
- `RoutingPlan/v1`, `runtime/risk_complexity.py`, `scorecard_routing.py`, `scorecard_shadow.py`, graph-aware impact e `ExpertisePack/v1` já existem.
- Contratos vivem em `src/apiforge/contracts/` como `VersionedContract` registrados em `contracts/registry.py`.
- Fixtures reutilizáveis em `tests/fixtures/`; `evals/corpus/` só tem README; `evals/cases/*.yaml` já é o formato de casos.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/context/gateway/`, `src/apiforge/economy/`, `src/apiforge/contracts/context.py`, `src/apiforge/evals/`, CLI + MCP mirrors | Estender módulos existentes; nenhum orquestrador paralelo |
| Relevant KB Domains | pydantic, testing, genai, prompt-engineering, anti-patterns, component-model, python | Contratos versionados, testes determinísticos, context engineering sem LLM |
| IaC Patterns | N/A | Core local-first, sem rede, sem SDK de provider |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Escopo: programa inteiro ou fatia? | Programa (arquitetura-alvo 6 ondas) + fatia P0 = Onda 0 (medição) + Onda 1 (Context Gateway) | `/define` captura só P0; demais ondas registradas como alvo |
| 2 | O que prova sucesso? | Redução medida + qualidade: corpus fixo antes/depois, bytes caem com evidência ≥ baseline; tokens só com transcript real | Exige baseline gravado antes de mudar comportamento + gate de recall |
| 3 | Quem consome o capsule primeiro? | MCP + CLI compact (verbos existentes + `expand`) | Runtime/supervisor e host assets ficam fora da P0 |
| 4 | Onde vivem objetos `ctx://`? | Repo-local `<root>/.apiforge/ctx/` sha256-addressed | Store compartilhado `~/.apiforge` adiado para Onda 2 |
| 5 | Qual corpus? | Fixtures existentes + ground truth novo (12 casos) em `evals/corpus/economy/` | Qualidade = recall de `required_refs` |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/{fastapi_orders,spring_orders,go_orders,grpc,openapi,compatibility,orders_agentic,dbaccess_app}` | 8 fixtures | Apps/contratos reais pequenos, multi-linguagem |
| Output examples | `evals/cases/*.yaml` | 2 | Formato de caso de eval a seguir |
| Ground truth | `evals/corpus/economy/*.yaml` (a criar) | 12 | `intent`, `target`, `required_refs`, `expected_findings?` |
| Related code | `src/apiforge/economy/`, `src/apiforge/context/`, `src/apiforge/application/funnel.py`, `src/apiforge/contracts/registry.py` | — | Ledger, tokens, funnel, registry a estender |

**How samples will be used:**
- Baseline: bytes do contexto atual (`context`/`brief`) por caso, gravado antes do gateway.
- Gate: `evidence_recall` do capsule vs `required_refs`; mediana de redução de bytes.
- Fixtures de teste para store/hash/dedup/expansão.

---

## Approaches Explored

### Approach A: Context Gateway nativo sobre peças existentes ⭐ Recommended

**Description:** Novo `context/gateway/` monta `ContextCapsule/v1` a partir de `ContextService` + `GraphImpactAssessment` + `ExpertisePack`; refs `ctx://` sha256 em `.apiforge/ctx/`; expansão progressiva L0–L4 com orçamento determinístico; ledger evolui para `RunLedger/v1` + `CostVector/v1` com atribuição por fonte; superfícies CLI/MCP `context capsule`, `context expand`, `economy stats`, `economy explain`; benchmark em `evals/corpus/economy/`.

**Pros:**
- Reaproveita ~60% do existente; core sem SDK, hostless, offline.
- Cada contrato novo entra no registry; refusals com `AF-*` catalogado.

**Cons:**
- Migração de schema do ledger sem quebrar `economy report`.
- Qualidade do capsule depende do grafo por fixture.

**Why Recommended:** padrão presente no código (`ContextService`, `economy/ledger`, contracts registry) + KB pydantic/testing. Confiança 0.90.

---

### Approach B: `forge-kernel` compartilhado com Spark Forge

**Description:** Portar Context Gateway do Spark Forge para pacote comum.

**Pros:**
- Implementação única.

**Cons:**
- Acoplamento cross-repo; contraria "não copiar código"; antecipa decisão `forge-kernel` em aberto; domínio API ≠ Spark.

---

### Approach C: Só medição (Onda 0) agora

**Description:** Entregar `RunLedger`/`CostVector` + baseline; gateway em ciclo separado.

**Pros:**
- Diff menor, baseline provado primeiro.

**Cons:**
- Não prova "redução medida + qualidade" escolhido como critério.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-27 |
| **Reasoning** | Liga peças existentes numa estratégia econômica sem novo orquestrador nem acoplamento cross-repo; entrega a prova escolhida |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | P0 = Onda 0 + Onda 1; ondas 2–6 como arquitetura-alvo | Medir antes de otimizar; context é maior ganho isolado | Programa inteiro num DEFINE; só Onda 0 |
| 2 | Consumidor P0 = CLI + MCP | Menor superfície, testável hostless | Runtime/supervisor; host assets |
| 3 | Store `ctx://` repo-local `.apiforge/ctx/` | Sem estado global, sem GC agora | `~/.apiforge` compartilhado; sem persistência |
| 4 | Qualidade é restrição, custo é otimização | Nunca compensar recall pior com bytes menores | Score ponderado custo×qualidade |
| 5 | Tokens só observados (transcript); sem transcript → `unresolved` | Invariante já em `economy/tokens.py` | bytes/4 como prova |
| 6 | Orçamento estourado → `unresolved` + `AF-CONTEXT-BUDGET-EXHAUSTED` | No silent fallback | Rebaixar contexto silenciosamente |
| 7 | `economy explain` determinístico (regras, sem LLM) | Não pagar tokens para explicar tokens | Resumo por LLM |
| 8 | Baseline gravado antes de ativar gateway | Comparação honesta | Medir baseline depois |
| 9 | Build: testes direcionados por task; suíte completa só ao final | Evita rodar tudo a cada task (pedido do usuário) | Suíte completa por task |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| `BudgetEnvelope/v1` multi-dimensão (calls, fanout, debate, reserva verificação) | P0 só precisa `context_bytes` + `max_level` | Yes — Onda 3 |
| Delta-first (git diff base/head) | Depende de grafo incremental; P0 usa target explícito | Yes — Onda 2 |
| CAS compartilhado `~/.apiforge`, incremental parsing/graph, invalidação por dependência | Store repo-local basta para provar ganho | Yes — Onda 2 |
| `EconomyPlan/v1`, perfis economy/balanced/deep, escalation ladder, stop conditions, quality floor no router | Sem consumidor runtime na P0 | Yes — Onda 3 |
| Lazy expertise, reviewer ROI, debate por capsule/delta, shadow budget | Agentics fora do escopo P0 | Yes — Onda 4 |
| Compact MCP separado, log/error slicing, RTK nativo, verb-first em host assets | Ganho principal vem do caminho da informação | Yes — Onda 5 |
| Matriz economy×balanced×deep, holdout, mutation | Corpus de 12 casos cobre P0 | Yes — Onda 6 |
| `doctor --economy`, query expansion, verification ladder, test selection, tiering/local model, ProviderCapability | Não necessários para prova P0 | Yes |

**Mantidos na P0 após revisão:** `economy explain`, dedup canônico+deltas.

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Arquitetura + fluxo L0–L4, store, dedup, ledger, superfícies | ✅ | "ok" | No |
| Benchmark, componentes, falhas `AF-*` | ✅ | "ok" + suíte só ao final | Yes — decisão #9 |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Agentes consumindo o API Forge recebem contexto bruto e sem atribuição de custo; não há como selecionar apenas a evidência relevante nem provar economia sem perda de qualidade.

### Architecture Target (6 ondas — registro, não escopo P0)
0 medir (RunLedger/CostVector) → 1 Context Economy (Gateway/Capsule/ctx://) → 2 Cache & Incremental → 3 Economic Routing (BudgetEnvelope/EconomyPlan/perfis) → 4 Selective Agentics → 5 Tool/Host Economy → 6 Economy Evals.

### P0 Scope (Draft)
- `ContextCapsule/v1`, `ContextRef/v1` (`ctx://sha256/…`: hash, source, revision, provenance, size) no registry.
- Níveis: L0 intent, L1 fingerprint (`ContextService`), L2 impact (`GraphImpactAssessment`), L3 capsule (refs + policies + expertise ids + unresolved), L4 focused (trechos por linha).
- Orçamento determinístico `context_bytes` + `max_level`; serialização canônica.
- Dedup: schema canônico + `parity`/`delta` para DTO/SDK.
- Store `.apiforge/ctx/<sha256>`; `expand` verifica hash.
- `RunLedger/v1` + `CostVector/v1` (`context_bytes`, `tool_result_bytes`, `expansions`, `cache_hits`, `duration_ms`, `observed_tokens|unresolved`) com `source ∈ {graph, contract, code, knowledge, filesystem}`; leitura retrocompatível do `economy.jsonl` legado.
- CLI + MCP: `context capsule`, `context expand`, `economy stats`, `economy explain`, `evals economy`.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Agent hosts (Claude/Codex/Devin) via MCP | Recebem contexto grande e redundante |
| Operador hostless via CLI | Não sabe onde o custo está |
| Mantenedor do API Forge | Não prova economia sem regressão de qualidade |

### Success Criteria (Draft)
- [ ] Baseline de bytes gravado para 12 casos antes do gateway.
- [ ] `evidence_recall` do capsule ≥ baseline em 100% dos casos.
- [ ] Redução mediana de bytes ≥ 40% (ajustável no /define).
- [ ] Tokens reportados só com `--transcript`; caso contrário `unresolved`.
- [ ] `economy stats` atribui bytes por fonte; `economy explain` justifica cada ref por regra.
- [ ] Todo refusal com `AF-*` + `field` + `unlock`, catalogado.
- [ ] `apiforge sdd check --root docs/sdd` verde; suíte completa verde (rodada uma vez ao final).

### Constraints Identified
- Sem SDK de provider em `src/`; sem rede; sem mutação live.
- Edições via `apply_patch`; testes + artefatos SDD atualizados juntos.
- `economy report` existente não pode quebrar.
- Build: testes direcionados por task; suíte completa só ao final.

### Error Codes (Draft)
`AF-CTX-REF-NOT-FOUND`, `AF-CTX-HASH-MISMATCH`, `AF-CONTEXT-BUDGET-EXHAUSTED`, `AF-CTX-GRAPH-UNAVAILABLE` (degradado explícito L0/L1 + unresolved).

### Out of Scope (Confirmed)
- Ondas 2–6 (ver Features Removed).
- Integração no runtime/supervisor/RoutingPlan.
- Reescrita de host assets/skills/agents.
- Extração de `forge-kernel`.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 (+ abordagem + YAGNI) |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 8 grupos |
| Validations Completed | 2 |
| Duration | ~1 sessão |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_ECONOMY_CONTEXT_GATEWAY.md`
