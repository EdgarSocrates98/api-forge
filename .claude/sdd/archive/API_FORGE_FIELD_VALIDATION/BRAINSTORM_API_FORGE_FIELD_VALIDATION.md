# BRAINSTORM: API Forge Field Validation + System Graph Inference

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_FIELD_VALIDATION |
| **Date** | 2026-09-28 |
| **Author** | brainstorm-agent (+ api-adversarial-critic review) |
| **Status** | ✅ Complete (Defined) |
| **Branch** | `sdd/new-forge` |

---

## Initial Idea

**Raw Input:** `prompt_evo_new_forge.md` — pausar expansão feature-driven, entrar em fase evidence-driven ("Field Validation / Dogfooding"): 20–40 tarefas reais em 12 cenários, ~15 métricas por execução, foco em "por que precisei sair do fluxo do API Forge?", gap analysis em 8 categorias, escolher ≤2 temas estruturais. Apostas prévias: (1) API System / Workflow Intelligence (OpenAPI+Arazzo+AsyncAPI+gRPC+code), (2) Contract-to-Runtime Intelligence (OTel).

**Context Gathered:**
- 178 commits, ~50 SDDs em `docs/sdd/`; economy architecture fechada (waves 0–8 + 3 hardenings).
- Telemetria já existe: `economy/run_ledger.py`, `CostVector.context_bytes|cache_hits|duration_ms` (`contracts/economy.py`), `BudgetEnvelope.provider_calls` + checkpoint (`runtime/supervisor.py:283,1263`), `summary.json.unresolved`, `economy/roi.py`.
- Evals só sintéticos: `evals/agentic_quality.py` com `FakeModelAdapter`, 7 casos em `evals/corpus/agentic-quality`; `evals/corpus/README.md` admite não provar cobertura de produção sem entradas reais.
- Precedente: dogfooding de `sdd classify` achou gap que testes unitários não pegaram (`.claude/sdd/archive/API_FORGE_ECONOMY_ROUTING/SHIPPED_2026-09-27.md:110`).
- System Graph embrionário: `workspace/graph.py` monta grafo multi-repo, mas relations são **declaradas** (`manifest.relations`), sem inferência. `contract_intel/models.py` já cobre openapi/grpc/asyncapi/graphql + `ContractImpact`. `adapters/asyncapi/extract.py` lê AsyncAPI 2.x/3.x. `adapters/otel/extract.py` agrega spans por rota. Arazzo ausente de `src/`.
- Fixtures atuais (`tests/fixtures/*_orders`) são de brinquedo.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/field/` (novo), `src/apiforge/workspace/` (inferência), `evals/corpus/field/`, `docs/field/` | Harness reusa economy/runtime; inferência estende workspace graph |
| Relevant KB Domains | agentspec: `data-quality`, `streaming`, `anti-patterns`; projeto: `api-forge-context`, `api-forge-sdd`, `api-forge-verification`, `api-forge-observability`, `api-forge-messaging` | Ledger/evidence, verificação independente, OTel, producer/consumer facts |
| IaC Patterns | N/A (offline, local-first) | Sem provider SDK em `src/`; sem mutação live |

---

## Critical Analysis (brainstorm-agent + api-adversarial-critic)

**Veredito conjunto:** direção aprovada; proposta original rejeitada como SDD executável — é visão, não spec.

| # | Risco | Evidência | Mitigação adotada |
|---|-------|-----------|-------------------|
| R1 | Falso DONE — entregável é processo | `sdd check` valida artefatos, não aprendizado | Harness + gap report gerado + gate de saída verificável |
| R2 | Viés de autoavaliação | AGENT_PROTOCOL exige crítico independente do executor | Verificador agente cego vs ground truth; critic revisa report |
| R3 | Estatística fraca (12 cenários × ~3) | "8 de 30" → IC95% ≈ 12–46% | 6 cenários × ≥5 tarefas; report com IC |
| R4 | Conclusão pré-escrita ("aposta antes dos dados") | `prompt_evo_new_forge.md:444` | Hipótese pré-registrada + critério de refutação |
| R5 | Sem corpus definido | Nenhuma amostra disponível hoje | Manifesto de corpus = primeira tarefa, commitado antes do 1º run |
| R6 | Specs com fonte não resolvida | Marcadores `:chatgpt-content-reference` em linhas 181, 218, 233, 235, 295 | Arazzo 1.1 / OpenAPI 3.2.1 / Overlay 1.1 / AsyncAPI 3.1 = `unresolved` até fonte primária |
| R7 | Métricas demais → atrito de anotação | 15 métricas, ~9 humanas | 5 automáticas + 5 humanas, `exit_reason` enum fechado |
| R8 | Backlog infinito / "Wave 10 disfarçada" | Sem gate na proposta | 30 tarefas OU 4 semanas; tema só qualifica com ≥5 tarefas em ≥2 repos |
| R9 | Trilha S contamina medição (escolha C) | Tarefas antes/depois medem ferramentas diferentes | Flag OFF em todos os runs baseline; A/B no fim |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Corpus de repos reais? | Mix público + próprio | Ground truth externo (fix commits/CVEs) + atrito real; exige anonimização de repos próprios |
| 2 | Quem anota? | Usuário + verificador agente | `api-verification-engineer` revalida cego; divergência → `unresolved`; critic revisa gap report |
| 3 | Quantos cenários? | 6 × ≥5 tarefas (~30) | Manutenção/bug, Evolução/breaking change, Segurança, Multi-repo, Incidente/observabilidade, Performance |
| 4 | Gate de saída? | 30 tarefas OU 4 semanas | Tema qualifica com ≥5 tarefas em ≥2 repos; senão `inconclusive` → estende corpus, sem feature |
| 5 | Amostras existentes? | Nenhuma | Montar corpus é tarefa #1; OpenTelemetry Demo como alvo âncora para incidente/multi-serviço |
| 6 | Abordagem? | C (A + System Graph em paralelo) | Duas trilhas: F (field) e S (inferência) |
| 7 | Isolamento de S? | Trilha isolada, flag OFF nos runs | A/B no fim: subset multi-repo re-run com flag ON → prova causal do tema |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | N/A → `docs/field/corpus.yaml` (a criar) | 0 | Repos alvo: OpenTelemetry Demo (multi-linguagem, Kafka, gRPC+HTTP, traces, feature-flag failures), 1–2 repos próprios, 1–2 OSS com fix/CVE conhecido |
| Output examples | `summary.json`, `economy.jsonl`, runtime checkpoint (existentes) | — | Fonte das métricas automáticas |
| Ground truth | N/A → por tarefa no corpus | 0 | Fix commit, CVE advisory, falha injetada por feature flag do OTel Demo |
| Related code | `economy/run_ledger.py`, `runtime/supervisor.py`, `workspace/graph.py`, `contract_intel/models.py`, `adapters/otel/extract.py`, `adapters/asyncapi/extract.py`, `economy/roi.py` | 7 | Reusar; não reimplementar telemetria |

**How samples will be used:**

- Ground truth por tarefa → `task_completed` e FP/FN verificáveis pelo verificador cego.
- Tarefas anonimizadas → casos de regressão em `evals/corpus/field/`.
- OTel Demo → cenários incidente/performance/multi-repo com causa conhecida.

---

## Approaches Explored

### Approach A: Harness mínimo + ciclo instrumentado ⭐ Recommended (by agent)

**Description:** Schema `apiforge/field-run/v1`; `apiforge field record|annotate|report` reusando ledger/summary/checkpoint; manifesto de corpus; hipótese pré-registrada; gap report com IC; gate de saída; export → `evals/corpus/field/`.

**Pros:**
- DONE verificável; métricas automáticas sem atrito.
- Resultado vira eval de regressão.

**Cons:**
- ~1 wave de código antes do uso.
- Risco de over-engineering do harness.

**Why Recommended:** Ledger/checkpoint/`economy roi` já existem (conf. 0.80–0.85, codebase pattern); precedente de dogfooding em ECONOMY_ROUTING.

---

### Approach B: Protocolo puro sem código

**Description:** Template markdown em `docs/field/`, anotação manual, relatório escrito.

**Pros:**
- Começa hoje; zero scope creep.

**Cons:**
- Métricas automáticas perdidas; sem gate verificável; não vira eval.

---

### Approach C: A + System Graph inference em paralelo ✅ Selected by user

**Description:** Approach A (trilha F) + trilha S: inferência de relations cross-repo (HTTP/gRPC client → operação de outro repo; producer/consumer de tópico via facts messaging existentes) como relations `inferred` com `confidence` + `provenance` em `workspace/graph.py`, atrás de flag desligada por padrão.

**Pros:**
- Não perde 4 semanas de calendário na aposta #1.
- A/B com/sem flag gera prova causal do valor do tema.

**Cons:**
- Contradiz parcialmente a tese "evidência antes de construir".
- Risco de contaminação da hipótese → mitigado por flag OFF + A/B.
- Mais superfície de código no mesmo SDD.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach C (com guardrail de isolamento) |
| **User Confirmation** | 2026-09-28, sessão de brainstorm |
| **Reasoning** | Usuário quer avançar aposta #1 em paralelo; agente recomendou A; guardrail "trilha isolada, flag OFF nos runs, A/B no fim" aceito para preservar validade da medição |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Reusar telemetria existente | ledger/checkpoint já têm provider_calls, context_bytes, cache_hits | Nova camada de telemetria |
| 2 | 6 cenários × ≥5 tarefas | Poder estatístico mínimo | 12 cenários × ~3 |
| 3 | Hipótese pré-registrada H1 + refutação | Evita conclusão pré-escrita | Gap analysis livre pós-hoc |
| 4 | Verificador agente cego + critic | AGENT_PROTOCOL: crítico ≠ executor | Autoanotação única |
| 5 | Gate 30 tarefas / 4 semanas; tema ≥5 tarefas em ≥2 repos | Evita backlog infinito | Ciclo aberto |
| 6 | System Graph = inferência `inferred` ≠ `declared`, flag OFF | Gap real é falta de inferência, não de workspace | BusinessFlow/Arazzo modelado já |
| 7 | Specs novas = `unresolved` até fonte primária | Citações sem fonte | Amarrar roadmap a versões não verificadas |
| 8 | `exit_reason` enum fechado (8 categorias de gap) | Reduz atrito e ambiguidade | 15 campos livres |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Parsing Arazzo / Overlay / OpenAPI 3.2 | Versões não verificadas; nenhuma tarefa provou necessidade | Yes |
| BusinessFlow como entidade de primeira classe | Trilha S começa com grafo inferido | Yes |
| Contract-to-Runtime Intelligence | Aposta #2; `adapters/otel` + `observability/health` cobrem baseline | Yes (via gap report) |
| Framework packs (Spring, FastAPI, Go, .NET, NestJS, Quarkus) | Proposta própria diz "sob demanda" | Yes |
| GraphQL, DX/onboarding, Enterprise governance | Sem evidência | Yes |
| Cenários: construção, arquitetura, migração, API+eventos isolado, CI/CD governance, REST↔gRPC | Poder estatístico; eventos cobertos por multi-repo/OTel Demo | Yes (próximo ciclo) |
| Métricas `wrong_context_loaded`, `missing_knowledge`, `missing_capability`, `verification_depth` como campos próprios | Colapsam em `exit_reason` enum | Yes |
| Visão "OAuth 2.1 em 20 repos → implementar e acompanhar" | North star, não MVP | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Escopo dentro/removido (YAGNI) | ✅ | "Sim, segue" | No |
| Fluxo e componentes | ✅ | "Sim, gera o documento" | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
API Forge evoluiu por features sem evidência de uso em repositórios reais; falta medir, de forma reprodutível e não enviesada, onde e por que o usuário sai do fluxo, para derivar o roadmap de frequências reais — enquanto a aposta System Graph avança isolada e é validada por A/B.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Owner/maintainer do API Forge | Roadmap guiado por intuição; sem dados de gap real |
| Engenheiro de API usando o Forge em multi-repo | Precisa explicar manualmente relação entre serviços |
| Verificador independente (agente/humano) | Sem ground truth nem registro estruturado para revalidar |

### Success Criteria (Draft)
- [ ] `docs/field/corpus.yaml` + `docs/field/hypothesis.md` commitados antes do 1º run (verificável por git log).
- [ ] Schema `apiforge/field-run/v1` com campos automáticos (provider_calls, context_bytes, cache_reuse, time_to_evidence, time_to_solution wall-clock) derivados sem nova telemetria.
- [ ] `apiforge field annotate` recusa valores fora do enum com código `AF-FIELD-*` catalogado + `field` + `unlock`.
- [ ] ≥30 field-runs OU 4 semanas, cobrindo 6 cenários × ≥5 tarefas e ≥3 repos distintos.
- [ ] 100% dos runs revalidados pelo verificador; divergências registradas como `unresolved`.
- [ ] `apiforge field report` emite contagens + IC95% por `exit_reason` × repo e veredito H1 (confirmada / refutada / inconclusive).
- [ ] Trilha S: relations `inferred` com `confidence` + `provenance`, flag OFF por padrão; A/B em subset multi-repo reporta delta de `manual_context_required` e `time_to_solution`.
- [ ] Tarefas anonimizadas exportadas para `evals/corpus/field/` e executáveis por evals.
- [ ] ≤2 temas qualificados (≥5 tarefas em ≥2 repos) → próximos SDDs; nenhum tema → `inconclusive`, sem feature nova.
- [ ] `apiforge sdd check --root docs/sdd` verde.

### Constraints Identified
- Sem provider SDK em `src/`; sem mutação live AWS/DB; offline/local-first.
- Repos próprios anonimizados (hash de repo, sem código sensível em `evals/corpus/`).
- Refusals com `AF-*` + `field` + `unlock`, catalogados.
- Métricas automáticas via ledger/summary/checkpoint existentes.
- Flag System Graph OFF durante todas as tarefas baseline.
- Versões Arazzo/OpenAPI 3.2.x/Overlay/AsyncAPI 3.1 = `unresolved` até fonte primária.
- Testes direcionados por task; suite completa só antes do ship.

### Out of Scope (Confirmed)
- Arazzo/Overlay/OpenAPI 3.2 parsing; BusinessFlow entity.
- Contract-to-Runtime Intelligence; framework packs; GraphQL; DX; enterprise governance.
- Novos agents/MCP tools/workflows além do comando `field` e da flag de inferência.
- Cenários construção/arquitetura/migração/CI-CD neste ciclo.

### Unresolved (carry to Define)
- Fonte primária das versões de spec citadas.
- Autorização/licença dos repos próprios e escolha final dos OSS.
- Tempo de relógio: `CostVector.duration_ms` soma emissões ≠ wall-clock → precisa timestamps início/fim.
- Valor de `k` para temas no A/B (subset size).

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 7 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 8 |
| Validations Completed | 2 |
| Duration | ~1 sessão |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_FIELD_VALIDATION.md`
