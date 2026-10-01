# BRAINSTORM: API Forge v1 Closure

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_V1_CLOSURE |
| **Date** | 2026-09-22 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** `/agentspec:brainstorm @prompt_evo_api_forge_v1.1.md` — fechar o prompt inteiro.

**Context Gathered:**
- `prompt_evo_api_forge_v1.1.md` está implementado e verde: 593 testes, ruff/mypy limpos, `check_release.py` PASS, todas as 16 FASEs cobertas.
- `prompt_evo_api_forge_v1.md` é o spec original que o v1.1 estende — a auditoria achou 9 gaps literais ainda abertos nele.
- O repo tem SDD próprio em `.superpowers/sdd/` e convenções firmes: facts com proveniência, findings citam `fact_id`, `absent`/`unresolved` nomeados, `run` é a única família que executa binários, nada é inferido.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/perf/`, `src/apiforge/index/`, `src/apiforge/autonomy/`, `src/apiforge/knowledge/`, `tests/labs/` | Novos verbos entram nos módulos existentes, seguindo o padrão CLI+dispatch+MCP |
| Relevant KB Domains | `knowledge/performance-methodology`, `knowledge/resilience`, `knowledge/data-access-patterns` | Packs já existem; evals ganham campo `type` |
| IaC Patterns | `model terraform`/`model sam` readers | Facts `infra.*` já alimentam o index de IaC |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual o alvo real do brainstorm, já que o v1.1 está verde? | Fechar os gaps do **v1** (arquivo original) | Escopo vira "v1-closure": 9 itens residuais, não features novas |
| 2 | Todos os gaps ou parte? | Todos — suggest_fix, performance memory, noise floor, 8 indexes, self-healing, modos de autonomia, eval vocab, lab matrix | Uma feature com 8 tasks ordenadas |
| 3 | Quais amostras existem para grounding? | As existentes bastam — fixtures de lab, exports OTLP, dumps AWS fake | Fixtures novos seguem o padrão sintético atual; nenhum artefato real externo é pré-requisito |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/` (redis_app, dbaccess_app, resilience_app, otel exports) | 5+ | Padrão sintético existente; novos labs seguem o mesmo shape |
| Output examples | Payloads `model otel`/`perf verdict` em `tests/perf/` | ~4 | Shape dos PerformanceRun/TestRecord já é contrato fechado |
| Ground truth | Catálogo de regras + `tests/labs/` | 100+ regras | rule_ids/fixture paths são a verdade para evals declarativos |
| Related code | `perf/compare.py`, `autonomy/`, `index/build.py` | — | Padrões a estender, nunca duplicar |

**How samples will be used:**
- Fixtures sintéticos alimentam os probes declarados nos `evals.yaml` (ground truth de rule firing).
- PerformanceRuns serializados servem de entrada para `search_performance_memory` e noise floor.
- O ledger de autonomia e facts existentes alimentam os 8 novos tipos de índice — sem extratores novos.

---

## Approaches Explored

### Approach A: Feature única "v1-closure" com tasks ordenadas ⭐ Recommended

**Description:** Um SDD feature cobrindo os gaps como tasks atômicas com teste, doc e commit próprios — o padrão já usado nos Specs E–I.

**Pros:**
- Gaps se reforçam entre si (suggest_fix consome indexes; self-healing consome performance memory).
- Um ciclo SDD; commits atômicos preservados.
- Reusa contratos existentes (ActionPlan, PerformanceRun, Budgets).

**Cons:**
- Escopo grande num único spec — mitigado por tasks sequenciadas com gates próprios.

**Why Recommended:** codebase pattern — Specs E–I fecharam exatamente assim (confidence 0.80, codebase pattern only; nenhum domínio da KB agentspec cobre esta plataforma).

---

### Approach B: Mini-features independentes

**Description:** Cada gap com seu ciclo SDD completo (discover→ship).

**Pros:**
- Máximo isolamento e review granular.

**Cons:**
- ~8 ciclos de overhead; dependências cruzadas (memory→suggest, index→self-healing) forçariam ordem rígida sem ganho real.

---

### Approach C: Implementação direta sem SDD

**Description:** Implementar os gaps sem spec.

**Why not recommended:** viola a disciplina do próprio repo — mudança não-trivial passa por SDD.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-22 |
| **Reasoning** | Coesão entre gaps + padrão estabelecido dos Specs E–I |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Lab matrix declarativa | 192 casos reais seriam propina; matriz `technology × case` em `tests/labs/matrix.yaml` apontando fixtures/evals existentes é honesta | Criar labs dedicados por célula |
| 2 | Indexes derivados, não extratores | Os 8 tipos novos derivam de facts já extraídos — zero código de parsing novo | Extratores dedicados por tipo |
| 3 | `suggest_fix` é composição pura | Emite ActionPlan/diff declarativo; aplicação pertence ao mutation path com policy gate | Verbo que executa a sugestão |
| 4 | Autonomia: alinhar ou ADR | v1 pede 5 modos (observe/recommend/sandbox/approved/continuous); implementados 3 — decidir por mapeamento ou ADR justificando | Ignorar a divergência |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Lab matrix como 192 casos executáveis | Declarada basta: evals apontam fixtures reais; células vazias ficam nomeadas, não fabricadas | Yes — células ganham fixtures conforme adapters crescem |
| "Verification lane" separada do debate/verifier | `debate` + `af-verifier` já cobrem verificação independente capaz de refutar | Yes — se uma lane dedicada provar necessidade |
| Extratores novos para os 8 tipos de índice | Facts existentes já carregam a informação | No — derivação é suficiente por construção |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Escopo (9 gaps do v1) | ✅ | "Fechar todos" | No |
| Approach A + ordem das tasks | ✅ | Confirmada | No |
| Design em 4 camadas | ✅ | "ok" | No |
| YAGNI | ✅ | Lab matrix declarativa | Yes — matrix como dados |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
O spec original `prompt_evo_api_forge_v1.md` tem 9 itens literais ainda não implementados; fechá-los sem reintroduzir escopo do v1.1 já coberto.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Operador do API Forge | Verbos pedidos pelo spec (`suggest_fix`, `search_performance_memory`) não existem |
| Avaliador do spec | Divergência silenciosa entre modos de autonomia pedidos (5) e implementados (3) |

### Success Criteria (Draft)
- [ ] `perf memory` persiste e busca PerformanceRuns por subject/tool/janela — sem inferência
- [ ] `perf compare`/verdict cita noise floor quando medido; delta < floor vira `inconclusive` nomeado
- [ ] `perf suggest` emite ActionPlan/diff e nunca aplica
- [ ] `index build` emite os 12 tipos de índice do v1 (4 atuais + 8 derivados de facts)
- [ ] Pipeline self-healing `detect→explain→propose→authorize→execute→verify→compare→accept|rollback` existe como runbook estruturado sob a policy engine
- [ ] Modos de autonomia alinhados aos 5 do v1 ou ADR registrando a divergência justificada
- [ ] `evals.yaml` carrega `type` no vocabulário fechado de 11 tipos; `knowledge check` valida
- [ ] `tests/labs/matrix.yaml` declara tecnologia × caso → fixture/eval; teste verifica cobertura declarada
- [ ] pytest + ruff + mypy + release gate verdes

### Constraints Identified
- Local-first: nenhum gap pode exigir rede ou chamada a modelo.
- Determinismo: mesmas entradas, mesmos bytes; noise floor medido, nunca assumido.
- `suggest_fix` nunca aplica — composição pura.
- Facts imutáveis com proveniência; ausência nomeada, nunca preenchida.

### Out of Scope (Confirmed)
- Reimplementar itens do v1.1 já verdes (spec proíbe: "Não reimplemente funcionalidades já entregues").
- Executores de eval que chamem modelo.
- Labs reais por célula da matriz (declarativa nesta rodada).
- Injeção de falhas real (chaos executa fora do API Forge).

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 3 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 3 |
| Validations Completed | 4 |
| Duration | ~15 min |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_V1_CLOSURE.md`
