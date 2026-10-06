# DEFINE: Intelligent Capability Routing

> Conectar elegibilidade determinística, ranking explicável, execução bounded, avaliação e atualização de scorecards para melhorar o routing futuro sem transformar histórico em autoridade de segurança.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING |
| **Date** | 2026-09-24 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O API Forge já declara capabilities, filtra elegibilidade, executa agentes bounded e calcula scorecards, mas ainda não conecta essas partes em um routing explicável que use resultados verificados para melhorar escolhas futuras. Isso limita a eficiência do runtime e dificulta auditar por que um agente foi escolhido, sem perder os guardrails de risco, evidência, policy e budget.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Maintainer de plataforma | Define perfis, policies, scorecards e limites do runtime | Precisa configurar a seleção sem duplicar regras em cada adapter ou superfície |
| Runtime supervisor | Orquestra tarefas, invocations e fallback | Precisa escolher entre capabilities elegíveis usando evidência histórica, custo e duração observados |
| Revisor de qualidade/governança | Audita execução, evidência, evals e decisões | Precisa reconstruir candidatos, rejeições, sinais, fallback e origem de cada scorecard |
| Desenvolvedor de API | Consome uma execução para evoluir uma API | Precisa de uma escolha eficiente, resultado verificável e gaps explícitos quando não há prova suficiente |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Filtrar capabilities determinística e explicitamente por estado, capability, risco, prerequisites, evidência, policy e budget antes de qualquer ranking |
| **MUST** | Ordenar apenas candidatos elegíveis por um ranking versionado e explicável que use scorecard, custo e duração somente quando observados |
| **MUST** | Conectar execução bounded, verificação/eval e atualização persistida do scorecard, preservando evidências, gaps, estados `REVIEW`/`BLOCKED` e `unresolved` |
| **MUST** | Emitir um trace de routing com requisitos, candidatos, rejeições, sinais, policy, escolha, fallback e proveniência |
| **SHOULD** | Reproduzir a mesma ordenação quando contratos, scorecards, observações e policy forem iguais |
| **SHOULD** | Permitir que o maintainer compare eficiência, segurança e qualidade sem confundir ausência de observação com valor zero |
| **COULD** | Adicionar o otimizador adaptativo da abordagem C depois que houver scorecards e ground truth operacional suficientes |

**Priority Guide:**
- **MUST** = MVP fails without this (non-negotiable for MVP)
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] 100% das decisões de routing no corpus de aceitação emitem um trace versionado com requisitos, candidatos, rejeições, sinais, policy, escolha e fallback.
- [ ] 0 capabilities inelegíveis são selecionadas no corpus de regressão, independentemente de scorecard, custo, duração ou heurística.
- [ ] 100% das capabilities selecionadas passam pelo filtro de elegibilidade antes do ranking e da execução.
- [ ] 100% dos scores de custo e duração usados no ranking possuem observação atribuível; valores ausentes permanecem explícitos e não são convertidos em zero.
- [ ] 100% dos scorecards atualizados referenciam pelo menos um resultado de eval persistido, seus cases de origem e evidências correspondentes.
- [ ] 0 scorecard updates transformam execução `BLOCKED`, ausência de evidência ou erro de eval em melhoria silenciosa de qualidade; `REVIEW` permanece distinguível de `PASS`.
- [ ] 100% dos replays com os mesmos inputs, scorecards, observações e policy produzem a mesma ordenação e o mesmo desempate.
- [ ] 100% dos casos obrigatórios de eval mantêm cobertura das categorias golden, holdout e mutation antes do gate passar.
- [ ] O baseline e o alvo numérico de melhoria de eficiência serão definidos no Design/Benchmark; até lá, o MVP deve registrar custo/duração observados e declarar `unresolved` quando não existirem.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Happy path de routing | Existem capabilities elegíveis, evidência necessária e scorecards válidos | O supervisor resolve a tarefa | O sistema filtra, ordena, escolhe e persiste trace com candidatos, sinais, policy e fallback |
| AT-002 | Capability inelegível | Uma capability está unsupported, desabilitada, sem prerequisite ou sem evidência | O routing é executado | A capability é rejeitada antes do ranking; ela nunca é selecionada e o motivo permanece no trace |
| AT-003 | Scorecard não autoriza | Um candidato possui scorecard superior, mas falha em risco ou policy | O ranking é calculado | O candidato é excluído pelo filtro e o scorecard não consegue promovê-lo |
| AT-004 | Dados de eficiência ausentes | Um candidato não possui custo ou duração observados | O ranking é calculado | O componente ausente fica `unknown`/`unresolved`, não vira zero, e a decisão informa a limitação |
| AT-005 | Scorecard inválido | O arquivo de scorecard não satisfaz o contrato | O registry carrega os scorecards | A operação retorna `AF-SCORECARD-INVALID` com `field` e `unlock`; não há atualização silenciosa |
| AT-006 | Scorecard ausente | Um candidato elegível não tem histórico persistido | O ranking é calculado | O candidato continua elegível, recebe fallback determinístico e o trace registra a ausência de histórico |
| AT-007 | Avaliação aprovada | Uma execução possui resultado eval persistido, evidências e verdict `PASS` | O ciclo de atualização é executado | O scorecard é atualizado com cases, evidências, dimensões e digest/proveniência |
| AT-008 | Avaliação não aprovada | A execução termina `REVIEW`, `BLOCKED`, com erro ou evidência insuficiente | O ciclo de atualização é executado | O resultado permanece explícito, gaps são preservados e não há melhoria silenciosa do scorecard |
| AT-009 | Replay determinístico | Existem os mesmos requisitos, candidates, scorecards, observações e policy | O routing é repetido | A ordenação e o desempate são idênticos e referenciam a mesma base de decisão |
| AT-010 | Falha e fallback | O candidato primário falha dentro do budget permitido | O scheduler propaga a falha | O fallback segue a ordem registrada, respeita policy e preserva o erro, a dependência e a decisão final |
| AT-011 | Ausência de capability elegível | Nenhum candidato satisfaz os requisitos | O supervisor tenta iniciar a execução | A operação permanece bloqueada com `AF-CAPABILITY-ELIGIBILITY`, `field`, `unlock` e gap `unresolved` |
| AT-012 | Gate de qualidade incompleto | Falta uma categoria obrigatória ou um caso mandatory no eval gate | O ciclo tenta publicar o scorecard | O gate retorna `AF-RUNTIME-EVAL-GATE`; o scorecard não é promovido como evidência de qualidade |
| AT-013 | Compatibilidade de artefatos | Existem scorecards e artifacts legados carregáveis | O novo routing lê e projeta os dados | Os dados continuam legíveis; incompatibilidade explícita não é tratada como sucesso |

---

## Out of Scope

Explicitly NOT included in this feature:

- Aprendizado online de pesos, bandit ou otimizador adaptativo no MVP.
- Knowledge Packs, freshness externa e especialização composicional nesta fatia.
- Estimador de complexidade e replanejamento adaptativo do DAG.
- Métrica agregada de Evidence Coverage e control plane TUI 2.0.
- Modularização total da CLI.
- Matriz ampliada de versões Python.
- Adapters reais de providers/modelos e mutações externas.
- Branch protection e governança externa do GitHub.
- Prometer melhoria percentual de eficiência antes de estabelecer baseline e benchmark observados.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Elegibilidade determinística deve preceder ranking | Nenhum scorecard, custo, duração ou heurística pode superar risco, policy, prerequisites ou evidência |
| Technical | O MVP é híbrido bounded | Histórico pode ordenar candidatos elegíveis, mas não concede autoridade de execução |
| Evidence | Métricas de custo, duração, qualidade e segurança precisam de observação atribuível | Ausência permanece `unknown`/`unresolved`; não há imputação silenciosa |
| Compatibility | Contratos e artifacts devem evoluir aditivamente | CLI, JSON, MCP e run artifacts existentes permanecem legíveis ou recusam com código explícito |
| Runtime | Execução usa supervisor, scheduler e budget atuais | O MVP não cria um segundo orquestrador nem um caminho de execução externo |
| Safety | Core continua offline-first e sem SDK de provider/modelo | Adapters fake/local são a prova inicial; integrações externas exigem boundary, receipt e policy próprios |
| Quality | Golden, holdout e mutation continuam obrigatórios | O ciclo não atualiza reputação sem eval persistido e evidência suficiente |
| Governance | Toda recusa pública mantém `AF-*`, `field`, `unlock` e `unresolved` quando aplicável | Operadores conseguem corrigir a entrada sem traceback ou sucesso ambíguo |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts`, `src/apiforge/runtime`, `src/apiforge/capabilities`, `src/apiforge/evals`, tests em `tests/runtime`, `tests/capabilities`, `tests/evals` | Estender o kernel existente; preservar registry, supervisor, scheduler, scorecard e eval gate |
| **KB Domains** | `genai`, `python`, `pydantic`, `testing`, `data-quality` | Consultar state machines, bounded orchestration, async determinístico, contratos validados, fixtures, evals e dimensões de qualidade |
| **IaC Impact** | None | A primeira fatia é offline-first e não cria recursos de infraestrutura |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `${CLAUDE_PLUGIN_ROOT}/kb/`
- **IaC Impact** → No infrastructure planning is required for the MVP

---

## Data Contract (if applicable)

This feature is not an ETL or analytics pipeline. The relevant data contract is an artifact contract for routing decisions, observations, eval results and scorecards.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| `src/apiforge/rules/agentic_runtime.yaml` | Local YAML registry | Unknown; measured by registry loader | Versioned with source | Runtime maintainers |
| `src/apiforge/rules/agent_profiles.yaml` | Local YAML profiles | Unknown; measured by loader | Versioned with source | Capability maintainers |
| TaskSpec/run artifacts | Local JSON/artifacts | Per run; exact scale unresolved | Created/observed per execution | Runtime supervisor |
| `tests/evals/cases/*.yaml` and eval results | Local YAML/JSON | Corpus size to be measured | Versioned per eval revision | Verification maintainers |
| `.apiforge/scorecards/*.json` | Local JSON scorecards | One or more per profile; exact inventory unresolved | Updated only after verified eval | Capability/eval service |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `routing_policy` | versioned identifier | Required for every decision | No |
| `candidate` | capability/agent identifier | Must reference registry/profile | No |
| `eligibility` | enum + reasons | Must be decided before ranking | No |
| `observed_signals` | structured values | Unknown values remain explicit | No |
| `ranking_key` | versioned structured value | Reproducible for same inputs | No |
| `decision` | selected/fallback/unresolved | Must include reason and evidence refs | No |
| `eval_refs` | tuple of case/evidence refs | Required for scorecard update | No |
| `scorecard_digest` | hash or unresolved | Must cover source cases and dimensions | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Registry/profile | Valid for the source revision | Source hash and version |
| Runtime observations | Valid only for the execution that produced them | Run id, timestamp and artifact hash |
| Scorecard | Valid for its computed cases and source artifacts | `computed_from`, evidence refs and digest |
| External ground truth | No MVP SLA | Admit only through an approved read-only path with freshness/receipt metadata |

### Completeness Metrics

- 100% das decisões de aceitação possuem policy, candidatos, escolha, fallback e evidências ou gaps explícitos.
- 100% dos scorecards possuem cases de origem, verdict, evidências e gaps preservados.
- 0 valores desconhecidos são convertidos silenciosamente em zero.
- 100% dos resultados usados no gate mantêm a categoria golden, holdout ou mutation correspondente.

### Lineage Requirements

- Cada decisão aponta para TaskSpec, policy, registry/profile revision e inputs observados.
- Cada ranking aponta para os scorecards e sinais usados, incluindo valores `unknown`.
- Cada scorecard aponta para cases de eval, evidências, gaps e digests dos resultados.
- Cada fallback aponta para a falha ou rejeição que o causou.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | `src/apiforge/runtime/registry.py` pode receber um ranking separado sem alterar a semântica de elegibilidade | Será necessário separar registry em uma facade de eligibility antes do ranking | [ ] |
| A-002 | `AgentScorecard` pode evoluir aditivamente para dimensões de custo, duração, segurança e verificação | Será necessário um contrato versionado novo e migração explícita dos scorecards | [ ] |
| A-003 | `EvalResult` e o runtime possuem evidências suficientes para atribuir resultado ao agente/capability | Scorecards terão de permanecer parciais e `unresolved` até um receipt adicional | [ ] |
| A-004 | O adapter fake pode produzir respostas determinísticas e expor observações opcionais de custo/duração | A prova de ranking de eficiência ficará limitada a fixtures de observação injetada | [ ] |
| A-005 | `.apiforge/scorecards/` é uma persistência adequada para o primeiro closed loop | Será necessário introduzir um store versionado antes do Design final | [ ] |
| A-006 | Requisitos de TaskSpec e evidência disponíveis bastam para reproduzir uma decisão | O contrato precisará de uma etapa de normalização ou de novos inputs obrigatórios | [ ] |
| A-007 | O baseline de eficiência pode ser medido em um benchmark local sem provider externo | A meta de eficiência permanecerá limitada a telemetria e ordenação relativa | [ ] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Problema, impacto e necessidade de routing explicável estão claros |
| Users | 3 | Maintainer, supervisor, revisor e desenvolvedor têm dores distintas e explícitas |
| Goals | 3 | Goals MUST/SHOULD/COULD cobrem elegibilidade, ranking, execução, eval e evolução futura |
| Success | 2 | Invariantes são mensuráveis, mas o alvo numérico de eficiência depende de baseline/benchmark ainda não observado |
| Scope | 3 | MVP, extensões futuras e exclusões estão delimitados pelo brainstorm confirmado |
| **Total** | **14/15** | Acima do gate; pronto para Design com a lacuna de eficiência registrada |

**Scoring Guide:**

- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Qual baseline de custo/duração será usado no benchmark local e qual melhoria mínima de eficiência justificará a mudança de routing?
- Quais dimensões exatas e pesos iniciais serão configuráveis no ranking, mantendo segurança como guardrail e não como preferência livre?
- O scorecard multidimensional será um contrato aditivo em `AgentScorecard` ou uma projeção vinculada por `profile_id`?
- Como o runtime distinguirá observação de duração/custo produzida pelo adapter fake de ground truth operacional externo?
- Quais campos de `TaskSpec` representam requisitos de capability de forma suficiente e quais precisam de normalização?

Essas perguntas não bloqueiam a captura de requisitos, mas devem ser resolvidas no Design/Benchmark antes de implementar ou declarar ganho de eficiência.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-24 | define-agent | Requirements derived from validated brainstorm; clarity 14/15 |
| 1.1 | 2026-09-24 | ship-agent | Shipped and archived |

---

## Next Step

**Archived:** `.claude/sdd/archive/INTELLIGENT_CAPABILITY_ROUTING/`
