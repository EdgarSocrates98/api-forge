# BRAINSTORM: Intelligent Capability Routing

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING |
| **Date** | 2026-09-24 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:**

The supplied evaluation in `prompt_evo_nova_avaliacao.md` identifies Intelligent Capability Routing as the next high-value evolution: combine capability requirements, agent candidates, scorecards, risk, cost and evidence; execute the selected plan; evaluate the result; and feed the verified outcome back into future routing. The prompt must not be committed.

**Context Gathered:**

- The runtime already has declarative capabilities, agent profiles, eligibility checks, scorecard persistence, a supervisor, a bounded scheduler and adaptive debate contracts.
- `src/apiforge/runtime/registry.py` filters candidates using profile state, accepted risks, prerequisites and available evidence, then currently orders eligible capabilities by scorecard quality.
- `src/apiforge/capabilities/scorecard.py` derives a scorecard from evaluation results and persists it under `.apiforge/scorecards/`.
- `src/apiforge/runtime/supervisor.py` connects eligibility to bounded execution, while `src/apiforge/evals/runtime_gate.py` preserves golden, holdout and mutation requirements.
- The desired MVP is a closed loop, but the adaptive optimizer is deferred until scorecards and operational ground truth are sufficiently established.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/contracts`, `src/apiforge/runtime`, `src/apiforge/capabilities`, `src/apiforge/evals`, with tests under `tests/runtime`, `tests/capabilities` and `tests/evals` | Extend the existing kernel and preserve the supervisor, scheduler, registry and eval boundaries |
| Relevant KB Domains | `genai`, `python`, `pydantic`, `testing`, `data-quality` | Use bounded state-machine orchestration, validated versioned contracts, deterministic async behavior, fixture-driven tests and explicit quality dimensions |
| IaC Patterns | Not applicable to the offline MVP | No infrastructure or provider mutation is needed; fake/offline adapters are sufficient for the first proof |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual objetivo deve guiar a primeira fatia: routing adaptativo, closed loop de eval/scorecard ou ambos? | Ambos, com uma primeira fatia vertical definida | O MVP precisa provar a ligação entre seleção, execução, avaliação e atualização histórica |
| 2 | Quem é o usuário principal? | Maintainer/plataforma e runtime supervisor, com o supervisor consumindo contratos definidos pelo maintainer | A solução deve servir configuração/governança e consumo automático sem duplicar semântica entre superfícies |
| 3 | Qual limite de decisão deve ser obrigatório? | Híbrido bounded: regras determinísticas filtram candidatos; sinais históricos apenas ordenam os elegíveis | O scorecard não pode autorizar uma capability nem superar risco, evidência, prerequisites ou policy |
| 4 | Qual resultado define sucesso? | Eficiência é o indicador primário; segurança tem peso quase equivalente; qualidade vem em seguida | O ranking deve otimizar custo/latência dentro de guardrails de segurança e manter prova de qualidade |
| 5 | Quais amostras devem fundamentar o MVP? | Fixtures/evals existentes, novos casos sintéticos e ground truth operacional quando disponível e anonimizável | A prova combina contratos já exercitados, falhas controladas e observações reais sem transformar ausência de dados em zero |

**Minimum Questions:** 5 (to ensure clarity before proceeding)

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting. For this feature they also provide deterministic routing ground truth; no operational claim is inferred from a fixture alone.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `src/apiforge/rules/agentic_runtime.yaml`, `src/apiforge/rules/agent_profiles.yaml`, existing TaskSpec and case artifacts | Existing repository set | Capability declarations, profile constraints, task requirements and evidence references |
| Output examples | `.apiforge/scorecards/*.json`, runtime run artifacts, supervisor responses | Existing repository set | Persisted scorecards, invocation outcomes, routing traces and gaps; exact inventory belongs in Define/Build |
| Ground truth | `tests/evals/cases/*.yaml`, `tests/capabilities/test_scorecard.py`, `tests/runtime/test_scheduler.py`, `tests/evals/test_runtime_evals.py` | Existing test corpus | Expected verdicts, required evidence, scheduler behavior and golden/holdout/mutation gate behavior |
| Related code | `src/apiforge/runtime/registry.py`, `src/apiforge/capabilities/scorecard.py`, `src/apiforge/runtime/supervisor.py`, `src/apiforge/evals/runtime_gate.py` | Existing modules | Reuse the current eligibility, execution, scorecard and eval authorities instead of creating parallel stores |
| Synthetic cases | To be added under `tests/fixtures` and `tests/evals/cases` | To be measured | Ranking ties, missing/invalid scorecards, fallback, evidence gaps, regressions and observed cost/latency absence |
| Operational ground truth | User-provided or collected through an approved local/read-only path | Optional | Agent outcomes, cost and duration are admitted only when observed, attributable and safe to anonymize |

**How samples will be used:**

- Existing runtime and capability tests will preserve current eligibility and scheduler behavior.
- Synthetic fixtures will exercise candidate ordering, stable tie-breaking, fallback and unresolved states.
- Golden, holdout and mutation cases will prevent a scorecard update from being accepted without the required evaluation evidence.
- Operational observations, when available, will calibrate cost and latency without treating unknown values as zero.
- Replays will compare routing decisions and scorecard updates using persisted contracts, evidence references and policy versions.

---

## Approaches Explored

### Approach A: Closed loop vertical híbrido ⭐ Recommended

**Description:** Normalize task requirements, filter capabilities deterministically by evidence/risk/policy/budget, rank eligible candidates using scorecards plus observed cost and latency, execute through the current bounded runtime, evaluate the result, and persist a scorecard update for future routing.

**Pros:**

- Delivers the requested routing-to-evaluation loop in one coherent slice.
- Reuses the existing registry, supervisor, scheduler and eval gate.
- Keeps eligibility deterministic while allowing historical evidence to improve ordering.
- Produces an explainable trace with candidates, rejected reasons, signals, fallback and evidence.

**Cons:**

- Requires versioned contracts for routing decisions, observations and scorecard updates.
- Early rankings may have sparse operational history and must expose that limitation.
- Cost and latency cannot participate until they are actually observed.

**Why Recommended:** The codebase already implements the major boundaries needed for this composition: eligibility in `src/apiforge/runtime/registry.py`, scorecard derivation in `src/apiforge/capabilities/scorecard.py`, bounded execution in `src/apiforge/runtime/supervisor.py` and quality gates in `src/apiforge/evals/runtime_gate.py`. The `genai` KB patterns for state-machine orchestration and evaluation align with this composition. Confidence: **0.95**, based on KB pattern plus direct codebase match.

---

### Approach B: Scorecards primeiro

**Description:** Expand multidimensional scorecards and evaluation storage first, leaving runtime selection mostly static until the scorecard model is mature.

**Pros:**

- Minimizes immediate changes to execution behavior.
- Allows metric definitions and ground truth to stabilize before routing consumes them.
- Simplifies early regression analysis.

**Cons:**

- Delays the user-visible benefit of intelligent routing.
- Does not prove the closed loop between scorecard history and future choices.
- Can produce a scorecard model disconnected from actual routing decisions.

---

### Approach C: Optimizer adaptativo

**Description:** Learn routing weights or candidate choices from historical outcomes using an adaptive heuristic or bandit-like optimizer, with a deterministic fallback.

**Pros:**

- Offers greater long-term optimization potential.
- Could learn domain-specific trade-offs between quality, cost and latency.
- Provides a future path after enough attributable observations exist.

**Cons:**

- Requires more history than the current evidence base guarantees.
- Makes regressions, explanations and policy review harder.
- Risks turning learned preference into implicit authority over safety constraints.

---

## Data Engineering Context (if applicable)

Not applicable as a data pipeline. Scorecards and routing observations are versioned local artifacts derived from verified evaluations. Operational observations remain read-only inputs; the MVP does not introduce a database, stream, ETL process or external mutation path.

### Source Systems

| Source | Type | Volume Estimate | Current Freshness |
|--------|------|-----------------|-------------------|
| Local runtime, eval cases and scorecard artifacts | Versioned files | Not established | Determined by artifact timestamps and hashes |
| Optional operational observations | Approved read-only adapter or user-provided data | Unknown | Must be observed and recorded; never inferred |

### Data Flow Sketch

```text
[TaskSpec + evidence] → [Eligibility] → [Ranking] → [Bounded runtime]
       → [Verification/eval] → [Scorecard artifact] → [Future ranking]
```

### Key Data Questions Explored

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | What is the expected data volume? | Unknown for the MVP | Keep storage local and deterministic; measure before selecting a broader persistence strategy |
| 2 | What freshness SLA is needed? | No external freshness SLA for the MVP | Use artifact timestamps/hashes and preserve unresolved freshness rather than inventing a window |
| 3 | Who consumes the output? | Runtime supervisor and platform maintainer | Provide machine-readable routing traces and maintainer-readable scorecard projections |

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — Closed loop vertical híbrido |
| **User Confirmation** | 2026-09-24 |
| **Reasoning** | O usuário confirmou A como MVP e adiou C; a primeira fatia deve provar routing, execução, avaliação e atualização de scorecard sem entregar autoridade a um otimizador aprendido |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Elegibilidade é determinística e precede o ranking | Segurança, prerequisites, evidência e policy não podem ser compensados por custo ou qualidade histórica | Ranking livre sobre todas as capabilities |
| 2 | Scorecard ordena candidatos, não autoriza capabilities | Mantém a separação entre capability contract, policy e reputação operacional | Usar `quality_score` como gate implícito |
| 3 | Eficiência é o objetivo primário, com segurança quase no mesmo peso e qualidade depois | Reflete a prioridade confirmada para custo/latência sem degradar controle | Otimizar somente qualidade média |
| 4 | Dados ausentes ficam explícitos e não viram zero | Custo, latência e qualidade precisam de observação atribuível | Imputar valores para forçar um ranking |
| 5 | A atualização do scorecard exige eval persistido e evidência | Evita reforçar reputação com execução não verificada ou `REVIEW`/`BLOCKED` sem ressalvas | Atualizar após qualquer execução |
| 6 | O MVP usa adapters fake/offline e mantém external providers fora do fluxo | Preserva o boundary offline-first e a governança do projeto | Chamar providers reais para gerar dados iniciais |
| 7 | O otimizador adaptativo fica para depois | Precisa de histórico suficiente, explicabilidade e controles adicionais | Aprender pesos durante a primeira fatia |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Otimizador/bandit e aprendizado de pesos | Não é necessário para provar o loop e não possui ground truth suficiente no MVP | Yes, after scorecard/evidence maturity |
| Knowledge Packs e freshness externa | Especialização de conhecimento não é necessária para validar a seleção bounded entre capabilities já declaradas | Yes |
| Estimador de complexidade e DAG adaptativo | O scheduler já fornece execução bounded; complexidade pode ser adicionada depois de observar padrões de tarefas | Yes |
| Evidence Coverage completo e dashboard de níveis | O MVP precisa preservar evidências e gaps, mas não precisa de uma métrica agregada ou nova UX | Yes |
| TUI 2.0 de control plane | A primeira prova deve estabilizar contratos e traces antes de ampliar a projeção visual | Yes |
| Modularização total da CLI | É dívida relevante, mas não é necessária para o closed loop nem para a segurança do ranking | Yes |
| Matriz ampliada de versões Python | Não altera a semântica do routing e exigiria uma matriz observada própria | Yes |
| Adapters reais de providers/modelos | Exigiriam boundaries, receipts e gates adicionais; fake/offline basta para a primeira prova | Yes, behind explicit gates |
| Branch protection e governança externa do GitHub | É uma lacuna operacional real, mas fica fora do kernel e do MVP de routing | Yes, as a separate governance initiative |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Núcleo da solução e fluxo `requirements → eligibility → ranking → execution → eval → scorecard` | ✅ | Ok; scorecard deve ordenar, não autorizar | No |
| Contratos, falhas e prova | ✅ | Ok; dados ausentes, scorecard inválido e `REVIEW`/`BLOCKED` devem permanecer explícitos | No |
| Corte YAGNI | ✅ | Ok; A entra no MVP e C fica para depois | No |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

O API Forge já consegue declarar capabilities, executar agentes bounded e calcular scorecards, mas ainda precisa conectar essas partes em um routing explicável que use resultados verificados para melhorar escolhas futuras sem transformar histórico em autoridade de segurança.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Maintainer de plataforma | Precisa declarar requisitos, políticas, pesos e limites de routing sem duplicar regras no runtime |
| Runtime supervisor | Precisa escolher entre capabilities elegíveis usando evidência histórica, custo e latência observados |
| Revisor de qualidade/governança | Precisa auditar por que uma capability foi selecionada, rejeitada ou substituída e como o scorecard foi atualizado |
| Desenvolvedor de API | Precisa receber uma execução eficiente com fallback explícito, evidências preservadas e gaps visíveis |

### Success Criteria (Draft)

- [ ] Cada decisão de routing produz uma entrada versionada com requisitos, candidatos, rejeições, sinais, política, escolha e fallback.
- [ ] Nenhuma capability inelegível é selecionada por causa de scorecard, custo, latência ou heurística.
- [ ] O ranking usa custo e duração apenas quando forem observados e atribuíveis; valores desconhecidos permanecem desconhecidos.
- [ ] A execução continua bounded e preserva invocation, status, dependências, artifacts, evidências, erros e gaps.
- [ ] Scorecards só são atualizados a partir de resultados de eval persistidos, incluindo evidências, cases de origem e dimensões calculadas.
- [ ] Resultados `REVIEW`, `BLOCKED`, conflitos e ausência de evidência não aumentam silenciosamente a reputação do agente.
- [ ] Replays reproduzem a mesma ordenação quando recebem os mesmos contratos, scorecards, observações e política.
- [ ] Golden, holdout e mutation continuam obrigatórios para a prova do ciclo.
- [ ] O fluxo permanece offline-first, sem SDK de provider/modelo no core e sem mutação externa.
- [ ] A solução mantém códigos `AF-*`, hashes, `unresolved` e limitações nas projeções JSON, CLI e futuras superfícies.

### Constraints Identified

- Elegibilidade determinística deve preceder qualquer ranking adaptativo.
- O MVP é híbrido bounded: scorecards podem ordenar, mas não remover gates de policy, risco e evidência.
- Custo, latência, qualidade e segurança só podem ser calculados a partir de observações com proveniência.
- Ausência de scorecard ou observação não pode ser convertida em zero ou em uma promessa de suporte.
- `AF-SCORECARD-INVALID`, `AF-CAPABILITY-ELIGIBILITY`, `REVIEW`, `BLOCKED` e `unresolved` precisam permanecer visíveis.
- O core deve continuar offline-first; adapters fake são a prova inicial.
- Novos contratos devem ser versionados, compatíveis e projetáveis sem duplicar semântica entre CLI, TUI, MCP e JSON.
- O prompt `prompt_evo_nova_avaliacao.md` é apenas entrada de brainstorming e não deve ser commitado.

### Out of Scope (Confirmed)

- Aprendizado online de pesos, bandit ou otimizador adaptativo no MVP.
- Knowledge Packs, freshness externa e especialização composicional nesta fatia.
- Estimador de complexidade e replanejamento adaptativo do DAG.
- Métrica agregada de Evidence Coverage e control plane TUI 2.0.
- Modularização total da CLI.
- Matriz ampliada de versões Python.
- Adapters reais de providers/modelos e mutações externas.
- Branch protection e governança externa do GitHub.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 discovery/sample questions, plus one approach clarification |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 9 deferred features |
| Validations Completed | 3 checkpoints; 2 minimum required |
| Duration | one interactive session |

---

## Next Step

**Archived:** `.claude/sdd/archive/INTELLIGENT_CAPABILITY_ROUTING/`
