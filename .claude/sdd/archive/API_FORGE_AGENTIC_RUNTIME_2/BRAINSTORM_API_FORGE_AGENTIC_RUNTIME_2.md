# BRAINSTORM: API Forge Agentic Runtime 2.0

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_RUNTIME_2 |
| **Date** | 2026-09-22 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** Evoluir o API Forge para um runtime agentico completo, capaz de coordenar agentes e subagents especializados na evolução de APIs, com revisão de tarefas, debates baseados em evidências, crítico adversarial, referee, execução segura, verificação independente e evals. A evolução futura deve suportar observabilidade com OpenTelemetry, Datadog e Dynatrace, gRPC, AWS e bancos, mas o primeiro incremento deve priorizar o Runtime Agentico 2.0.

**Context Gathered:**
- O projeto já possui `TaskSpec`, planner, máquina de estados, dispatch determinístico, debate com quorum/referee, verifier, holdout, mutation checks, sandbox e briefs `DONE/REVIEW/BLOCKED`.
- Existem 20 perfis de agentes, 10 skills canônicas, 37 knowledge packs, fixtures para Spring, Go, FastAPI, OpenAPI, OTel e relatórios de ferramentas.
- O dispatch e o debate atuais persistem contratos e executam operações determinísticas, mas ainda falta um supervisor que coordene adapters de modelos, fan-out dinâmico, crítico, debate seletivo e avaliação de trajetória.
- O núcleo deve permanecer local-first, sem SDK de modelo obrigatório, sem mutações externas e com evidência como base de cada decisão.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/runtime`, `src/apiforge/agents`, `src/apiforge/contracts`, `src/apiforge/evals` | Introduzir o runtime sem substituir `taskspec`, `debate`, `dispatch` ou `verification`; integrar por contratos versionados. |
| Relevant KB Domains | `genai`, `testing`, `pydantic`, `python`, `terraform` | Usar Supervisor, State Machine, Tool Calling, Guardrails, Plan-and-Execute e evaluation framework; validar saídas com schemas. |
| IaC Patterns | AWS/Terraform/SAM existem como adapters e análise offline | AWS e infraestrutura permanecem fora do primeiro slice; criar interfaces read-only para extensões futuras. |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual é o objetivo principal do primeiro incremento? | Runtime Agentico 2.0 com orquestrador, revisão, especialistas, debates, crítico, referee e evals. | O foco é coordenação verificável, não Datadog, Dynatrace ou gRPC isoladamente. |
| 2 | Quem é o usuário primário? | Time de engenharia. | Handoffs, colaboração, histórico, decisões auditáveis e revisão independente são requisitos centrais. |
| 3 | Qual é o limite de autonomia? | Local + CI, sem mutações externas. | AWS, bancos, produção e ambientes compartilhados ficam read-only ou fora do slice. |
| 4 | Qual cenário prova o sucesso? | Evolução de uma API existente. | O fluxo deve partir de contrato/código/testes existentes e provar uma mudança em sandbox. |
| 5 | Quais amostras estarão disponíveis? | Ambas: fixtures locais e, no futuro, repositório real anonimizado; ainda não há amostra real. | Fixtures locais são o ground truth inicial; amostra real será uma lacuna explícita, não evidência inventada. |
| 6 | Qual arquitetura de orquestração? | Supervisor determinístico com adapters de modelos. | O core governa estados e políticas; providers são adapters opcionais. |
| 7 | Qual adapter de modelo entra primeiro? | Adapter fake determinístico + um provider real opcional. | CI não depende de rede/custo; integração real pode ser validada sob demanda. |
| 8 | Como executar especialistas? | Paralelismo dinâmico amplo, governado por orçamento, risco, dependências, timeout e concorrência. | O supervisor escolhe fan-out; a política impede paralelismo ilimitado e mantém replay. |
| 9 | Quando abrir debate? | Por gatilhos de risco/divergência ou por solicitação humana de sala de debate. | Debate não é obrigatório para tarefas simples, mas decisões controversas têm uma rota formal. |
| 10 | Quando usar crítico adversarial? | Sempre em mudanças de alto risco e antes da decisão final. | Segurança, dados, contratos, performance, infraestrutura, migração e impacto externo exigem crítica independente. |
| 11 | Quando exigir aprovação humana? | Somente em gates críticos. | Promoção, breaking change, segurança, dados, infraestrutura, ações externas, baixa confiança ou debate não resolvido pausam o fluxo. |

**Minimum Questions:** 11

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/orders_agentic/` | 4 | API FastAPI representativa com OpenAPI, dados, mutações e cenário de verificação. |
| Input files | `tests/fixtures/spring_orders/`, `tests/fixtures/go_orders/`, `tests/fixtures/fastapi_orders/` | 3 suites | APIs existentes em Java/Spring, Go e Python/FastAPI para generalização progressiva. |
| Output examples | `.apiforge/case/` e contratos em `docs/contracts/` | N/A | TaskSpec, TaskPlan, VerificationRecord, HoldoutRecord, receipts e briefs serão os schemas de saída. |
| Ground truth | `tests/fixtures/orders_agentic/mutations.yaml` e testes existentes | N/A | Falhas deliberadas, holdouts e assertions verificáveis para medir decisões corretas. |
| Related code | `src/apiforge/taskspec/`, `src/apiforge/debate/`, `src/apiforge/dispatch/`, `src/apiforge/verification/` | N/A | Componentes existentes a integrar no runtime. |
| Real repository | Ainda não disponível | 0 | Será adicionado posteriormente, anonimizado e validado antes de ser usado como evidência. |

**How samples will be used:**

- Executar o fluxo completo em uma evolução de API existente com resultado determinístico.
- Exercitar fan-out entre especialistas de contrato, segurança, performance, dados e arquitetura.
- Validar debates com posições conflitantes apoiadas por `fact_id`.
- Verificar que o crítico detecta mutações deliberadas e que o verifier não aceita falso `DONE`.
- Comparar trajetórias do adapter fake com um provider real opcional.
- Medir custo, cobertura de evidências, roteamento, bloqueios e qualidade dos handoffs.

---

## Approaches Explored

### Approach A: Supervisor determinístico com adapters de modelos ⭐ Recommended

**Description:** Máquina de estados própria do API Forge coordenando TaskSpec Reviewer, planner, especialistas em paralelo, merge de evidências, crítico adversarial, sala de debate, referee, sandbox, verifier e evals. O core não importa SDKs de modelos.

**Pros:**
- Reutiliza os contratos e estados já existentes.
- Funciona com Claude, GPT, Devin e Copilot por adapters.
- Facilita auditoria, replay, CI, orçamento e segurança.
- Preserva a arquitetura `deterministic-core + agentic orchestration`.
- Permite paralelismo dinâmico sob política.

**Cons:**
- Exige construir o runtime e contratos de trajetória.
- A integração inicial com providers será menor que em frameworks completos.

**Why Recommended:** O código existente já possui as peças principais — TaskSpec, dispatch, debate, sandbox e verifier — e a KB de `genai` recomenda estados explícitos, supervisor, tool calling validado e plan-and-execute. Confiança: **0,95** por correspondência entre padrão KB e código do projeto.

---

### Approach B: LangGraph como runtime principal

**Description:** Usar LangGraph como motor central de StateGraph, subgrafos, checkpoints e human-in-the-loop.

**Pros:**
- Fornece execução durável, subgrafos, interrupções e replay.
- Reduz o código inicial do orquestrador.

**Cons:**
- Introduz dependência forte no core.
- Pode conflitar com a máquina de estados e contratos do API Forge.
- Não resolve sozinho evidência, TaskSpec, mutação, holdout ou política.

**Why not recommended:** Pode ser um adapter futuro, mas não deve ser a fonte de verdade do estado nem limitar o suporte multi-modelo.

---

### Approach C: Swarm/mesh de agentes

**Description:** Agentes delegam dinamicamente uns aos outros em uma rede de especialistas.

**Pros:**
- Flexibilidade para problemas desconhecidos.
- Delegação dinâmica e exploração ampla.

**Cons:**
- Mais custo e risco de loops.
- Auditoria, responsabilidade e replay tornam-se mais difíceis.
- Maior superfície para excessive agency e prompt injection.

**Why not recommended:** Deve ser uma capacidade futura limitada por política, não o modo padrão do primeiro slice.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — Supervisor determinístico com adapters de modelos |
| **User Confirmation** | 2026-09-22 |
| **Reasoning** | Conecta as capacidades já implementadas em um ciclo agentico auditável, preservando determinismo, segurança local/CI e compatibilidade entre providers. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Core próprio baseado em máquina de estados | O API Forge precisa governar estados, evidências e políticas independentemente do modelo. | LangGraph como dependência obrigatória. |
| 2 | Adapter fake obrigatório e provider real opcional | Testes e CI devem ser determinísticos e econômicos. | Múltiplos providers reais obrigatórios. |
| 3 | Fan-out dinâmico sob política | Complexidade e risco variam por atividade, mas custo e segurança precisam de limites. | Paralelismo irrestrito. |
| 4 | Debate seletivo | Debate só agrega valor quando há risco, divergência ou pedido humano. | Debate em toda tarefa. |
| 5 | Crítico obrigatório em alto risco | Consenso não substitui tentativa independente de reprovação. | Crítico somente após divergência. |
| 6 | Aprovação humana em gates críticos | Mantém autonomia útil sem liberar mutações externas ou decisões perigosas. | Aprovação após toda execução ou autonomia total. |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Datadog e Dynatrace nativos | O primeiro slice deve provar coordenação; observabilidade entra como adapter OTel posterior. | Yes |
| gRPC completo, codegen e streaming | É uma especialização de protocolo, não necessária para provar o runtime. | Yes |
| AWS/bancos com mutação | Escopo escolhido é local + CI read-only. | Yes |
| LangGraph como core | Evita lock-in e preserva contratos próprios. | Yes, as optional adapter |
| Swarm/mesh irrestrito | Risco de loops, custo e baixa auditabilidade. | Yes, policy-bounded |
| Múltiplos providers reais obrigatórios | Rede e custo não podem tornar o CI instável. | Yes |
| Autonomia contínua em ambientes compartilhados | Ainda não há gates operacionais, rollback e observabilidade suficientes. | Yes |
| UI web | CLI/MCP e artefatos persistidos são suficientes para o primeiro slice. | Yes |
| Repositório real anonimizado como aceite | Ainda não existe amostra disponível. | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | Usuário confirmou o Supervisor determinístico, local + CI e evolução de API existente. | Yes — debate e providers ficaram seletivos. |
| Component breakdown | ✅ | Usuário confirmou Runtime Kernel, Supervisor, adapters, registry, Decision Room e Verification/Evals. | Yes — paralelismo tornou-se dinâmico sob política. |
| YAGNI scope | ✅ | Usuário confirmou features externas e integrações avançadas como deferidas. | No — escopo removido registrado. |

**Minimum Validations:** 2

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

O API Forge possui especialistas e mecanismos determinísticos isolados, mas precisa de um Runtime Agentico 2.0 que transforme a evolução de uma API existente em uma trajetória coordenada, auditável e verificável por múltiplos agentes, sem depender de um provider de modelo ou executar mutações externas.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Time de engenharia | Precisa coordenar especialistas, revisar decisões, compartilhar contexto e provar que uma evolução de API é segura. |
| Engenheiro responsável pela mudança | Precisa receber plano, evidências, execução em sandbox e decisão final clara. |
| Revisor técnico | Precisa verificar TaskSpec, riscos, provas, debates, holdouts e rollback sem confiar apenas em texto do agente. |
| Pipeline CI | Precisa executar o fluxo sem rede obrigatória, com resultados determinísticos e estados `DONE/REVIEW/BLOCKED`. |

### Success Criteria (Draft)

- [ ] Uma intenção de evolução de API existente gera um `RunRecord` persistido e um TaskSpec revisado/selado.
- [ ] O supervisor seleciona especialistas por capability e pode executar tarefas independentes em paralelo sob orçamento e limites.
- [ ] Cada agente produz artefato estruturado com fatos, premissas, evidências, riscos e próximo passo.
- [ ] O sistema inicia debate automaticamente por risco/divergência ou por solicitação humana de sala.
- [ ] Mudanças de alto risco passam por crítico adversarial antes do referee.
- [ ] O fluxo executa somente em sandbox/local/CI e recusa mutações externas não aprovadas.
- [ ] O verifier independente, holdout e mutation check conseguem recusar falso `DONE`.
- [ ] O adapter fake executa o cenário sem rede; provider real é opcional e observável.
- [ ] A trajetória registra agentes, tools, handoffs, tokens, latência, decisões e evidências.
- [ ] O brief final informa `DONE`, `REVIEW` ou `BLOCKED` com gaps e ação humana.
- [ ] Testes de contrato, replay, falhas, timeout, orçamento, divergência e segurança passam no CI.

### Constraints Identified

- Core sem import de SDK de modelo.
- Execução local-first e CI-safe.
- Nenhuma mutação AWS, banco, produção ou ambiente compartilhado no primeiro slice.
- Evidência estruturada e proveniência obrigatória.
- Paralelismo dinâmico limitado por política.
- Provider fake determinístico obrigatório.
- Aprovação humana apenas em gates críticos.
- Debates e crítico adversarial seletivos conforme risco e divergência.
- Compatibilidade futura com Claude, GPT, Devin e Copilot.

### Out of Scope (Confirmed)

- Datadog, Dynatrace e observabilidade vendor-specific.
- Implementação completa de gRPC, codegen e streaming.
- Execução real em AWS e bancos.
- LangGraph como dependência principal.
- Swarm/mesh sem limites.
- Multi-provider real obrigatório.
- Deploy autônomo, rollout ou rollback em produção.
- UI web.
- Repositório real anonimizado como requisito inicial.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 11 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 9 |
| Validations Completed | 2 |
| Duration | 2026-09-22 session |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_AGENTIC_RUNTIME_2/`
