# BRAINSTORM: Intelligent Capability Routing Follow-ups

> Exploratory session to clarify the roadmap for the capabilities deferred from the first Intelligent Capability Routing slice.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS |
| **Date** | 2026-09-24 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** Brainstorm de tudo que ficou de fora da primeira fatia: otimizador/bandit e aprendizado de pesos; Knowledge Packs e freshness externa; estimador de complexidade e DAG adaptativo; métrica completa de Evidence Coverage; TUI 2.0; modularização total da CLI; matriz Python ampliada; adapters reais de providers/modelos; branch protection e governança externa do GitHub.

**Context Gathered:**

- A primeira fatia de Intelligent Capability Routing foi implementada, validada e arquivada em `.claude/sdd/archive/INTELLIGENT_CAPABILITY_ROUTING/`.
- O repositório já possui contratos de evidência, tarefas, integrações externas, knowledge freshness, runtime gates, adapters locais, planner/matrix de migração e receipts para fronteiras externas.
- A CLI ainda é uma superfície ampla e parcialmente monolítica; há TUI existente, portanto a evolução deve consumir contratos compartilhados em vez de duplicar regras de domínio.
- A política do projeto mantém providers, GitHub, produção, branch protection e mutações externas atrás de adapters, workflows e policy gates; a ausência de evidência externa deve continuar explícita.
- O prompt original `prompt_evo_nova_avaliacao.md` não faz parte desta mudança e permanece intocado.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/contracts`, `knowledge`, `evals`, `integrations`, `application`, `migration`, `runtime`, `cli.py`, `cli_tui.py` | A definição deve separar contratos de domínio, orquestração, adapters e superfícies operacionais. |
| Relevant KB Domains | `genai`, `data-quality`, `python`, `pydantic`, `testing`, `airflow`, segurança/governança | Avaliação, observabilidade, guardrails, arquitetura em camadas, testes de integração e DAGs devem orientar as fatias. |
| IaC Patterns | Não aplicável ao core; políticas de CI/GitHub são externas | Governança externa deve ser representada por configuração, workflow dedicado e receipts, não por mutação no aplicativo. |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | O objetivo principal é eficiência, autonomia, governança ou uma combinação? | **C — combinação de eficiência/autonomia e plataforma/governança, ordenada por dependências.** | O roadmap precisa cobrir runtime e plataforma sem transformar os nove itens em uma entrega única. |
| 2 | Quem são os usuários prioritários? | **C — maintainers/operadores e plataforma/DevEx/CI; runtime primeiro, governança depois.** | As primeiras ondas devem produzir provas úteis para operação; UX e governança consomem contratos estabilizados. |
| 3 | Qual restrição domina as decisões? | **A — segurança, evidência e reversibilidade.** | Toda capacidade deve ter fallback, budget, receipt ou replay e uma forma clara de não promoção. |
| 4 | Que amostras estarão disponíveis para orientar a evolução? | **A — scorecards, routing traces, avaliações golden/holdout/mutation e fixtures locais; ainda sem telemetria externa.** | Otimização e claims sobre providers ficam bloqueados até haver dados independentes e verificáveis. |

**Minimum Questions:** 4

---

## Sample Data Inventory

> Os samples atuais são locais e reproduzíveis. Não há telemetria externa suficiente para sustentar aprendizado online, freshness de provider ou claims de produção.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/`, fixtures de avaliação e casos em `.apiforge/case/` | Não quantificado | Entradas locais para routing, contratos, receipts e gates. |
| Output examples | `src/apiforge/contracts/`, traces de routing e relatórios SDD arquivados | Inventariado | Estruturas tipadas de decisão, evidência, integração e plano. |
| Ground truth | Testes golden/holdout/mutation existentes e scorecards | Parcial | Há base para regressão; a cobertura completa para otimização ainda precisa ser definida. |
| Related code | `src/apiforge/knowledge`, `integrations`, `migration`, `runtime`, `evals`, `cli.py`, `cli_tui.py` | Inventariado | Precedentes para freshness, receipts, planner, adapters locais, gates e superfícies operacionais. |

**How samples will be used:**

- Reproduzir decisões com os mesmos inputs, versões e policies.
- Comparar plano estático, plano adaptativo e modo shadow sem depender de providers reais.
- Calibrar Evidence Coverage e scorecards contra golden, holdout e mutation checks.
- Validar contratos e adapters com fixtures locais antes de qualquer integração externa.
- Detectar regressões de CLI/TUI e compatibilidade de matriz Python sem converter ambientes não testados em suporte declarado.

---

## Approaches Explored

### Approach A: Roadmap por Gates de Evidência ⭐ Recommended

**Description:** Organiza os nove itens por dependência e maturidade: primeiro medição, contexto e fronteiras seguras; depois planejamento adaptativo; então otimização controlada; por fim superfícies operacionais e governança externa.

**Pros:**

- Evita otimizar sobre dados pobres ou transformar ausência de freshness externa em certeza.
- Preserva fallback determinístico, replay, holdout, mutation checks e reversibilidade.
- Aproveita contracts, receipts, freshness, scorecards e traces já existentes.
- Permite que CLI, TUI, providers e GitHub evoluam sobre contratos estáveis.

**Cons:**

- O valor completo de autonomia aparece em etapas.
- Exige disciplina para manter as primeiras integrações em modo observado ou simulado.
- A modularização da CLI e a TUI 2.0 ficam depois das decisões de domínio mais importantes.

**Why Recommended:** É a abordagem mais compatível com a restrição dominante de segurança, evidência e reversibilidade e com a ausência atual de telemetria externa confiável.

---

### Approach B: Verticais End-to-End

**Description:** Entrega verticais completas, combinando contexto, adapters, Evidence Coverage, DAG, otimização e superfícies operacionais em fatias de valor visível.

**Pros:**

- Produz feedback de usuário mais cedo.
- Exercita runtime, UX e integração em conjunto.
- Pode revelar rapidamente problemas de acoplamento entre contratos e superfícies.

**Cons:**

- Aumenta o acoplamento entre runtime, CLI/TUI, providers e governança.
- Torna regressões e causas de falha mais difíceis de atribuir.
- Pode pressionar a adoção de adapters reais ou aprendizado antes de haver evidência suficiente.

---

### Approach C: Plataforma e Governança Primeiro

**Description:** Começa pela modularização da CLI, TUI 2.0, matriz Python, adapters e integração com governança externa; só depois adiciona complexidade, DAG adaptativo e otimização.

**Pros:**

- Melhora cedo a ergonomia de operadores, DevEx e CI.
- Cria uma superfície de integração mais organizada para futuras capacidades.

**Cons:**

- Pode cristalizar APIs e UX antes de o comportamento adaptativo estar definido.
- Aumenta a área de mudança sem elevar primeiro a qualidade das provas.
- Branch protection e políticas externas continuariam dependentes de configuração e evidência fora do core.

---

## Data Engineering Context (if applicable)

### Source Systems

| Source | Type | Volume Estimate | Current Freshness |
|--------|------|-----------------|-------------------|
| Repositório e fixtures locais | Arquivos, YAML, testes e traces | Local; não quantificado | Reprodutível por checkout/caso |
| Knowledge Packs futuros | Artefatos versionados e metadados | A definir | Deve ser explícita por pack/versão |
| Providers/modelos futuros | Adapter externo read-only ou execução opt-in | Não observado | Desconhecida até receipt independente |
| GitHub e CI futuros | API/host workflow de governança | Não observado | Depende de receipt e configuração externa |

### Data Flow Sketch

```text
[Request]
    → [Deterministic Routing]
    → [Knowledge/Freshness + Evidence Context]
    → [Static or Adaptive Plan]
    → [Local Replay / Shadow / External-Read Adapter]
    → [Scorecard + Receipt + Trace]
    → [Promotion Gate or Deterministic Fallback]
```

### Key Data Questions Explored

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Existe telemetria suficiente para aprender pesos? | Ainda não; existem traces, scorecards e fixtures locais, mas não uma base externa independente. | Bandit deve começar offline ou em shadow, após baseline e holdout estáveis. |
| 2 | O que significa freshness neste programa? | Idade e origem verificáveis do insumo, separadas de validade ou correção do conteúdo. | Knowledge Packs e adapters precisam emitir freshness explícita sem elevar o sinal a verdade. |
| 3 | Como um DAG adaptativo permanece seguro? | Só pode escolher entre tarefas permitidas, com dependências, budget, timeout e fallback determinados. | O estimador não pode ampliar autoridade nem remover gates críticos. |
| 4 | Quem controla governança externa? | Workflow dedicado, credencial mínima e policy de repositório; não o core nem agentes. | Branch protection e mutações GitHub permanecem boundary externo com receipts. |

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — Roadmap por Gates de Evidência |
| **User Confirmation** | 2026-09-24, confirmado na sessão |
| **Reasoning** | Atende runtime e plataforma em ordem de dependência, priorizando segurança, evidência e reversibilidade; não exige providers reais ou telemetria externa antes de haver contratos e baselines. |

### Proposed Roadmap Waves

#### Onda 0 — Contrato de medição e segurança

- Consolidar eventos de decisão, fallback, custo/latência observados, resultado de avaliação e versão dos insumos.
- Definir o núcleo inicial de Evidence Coverage para decisões críticas.
- Formalizar replay, holdout, mutation check, budget, timeout e rollback.
- Manter adapters externos em boundary read-only, com freshness e receipts.

#### Onda 1 — Contexto confiável

- Introduzir Knowledge Packs versionados, locais e reproduzíveis.
- Expor freshness explícita sem confundir atualidade com verdade.
- Adicionar adapters reais de providers/modelos somente para capability discovery, observação controlada e execução opt-in.
- Registrar disponibilidade, versão, limites e falhas sem claims de produção.

#### Onda 2 — Planejamento adaptativo

- Adicionar estimador de complexidade determinístico e conservador.
- Permitir DAG adaptativo apenas dentro de políticas, dependências seladas, timeout, budget e fallback.
- Comparar plano estático e adaptativo com os mesmos fixtures e holdouts.
- Expandir Evidence Coverage para explicar a justificativa de cada rota.

#### Onda 3 — Otimização com aprendizado restrito

- Congelar baseline e conjunto de avaliação.
- Ajustar pesos primeiro offline.
- Executar bandit somente em shadow/simulation antes de qualquer promoção.
- Promover apenas após gates independentes de qualidade, segurança, custo, regressão e reversibilidade.

#### Onda 4 — Superfície operacional

- Modularizar a CLI incrementalmente por bounded contexts.
- Fazer a TUI 2.0 consumir contratos estabilizados.
- Ampliar a matriz Python somente para ambientes executados e declarados.
- Explicitar compatibilidade, degradação e suporte observado.

#### Onda 5 — Governança externa

- Representar branch protection, required checks, reviewers, ambientes e políticas como configuração externa.
- Integrar por receipts e leitura verificável.
- Permitir mutação somente pelo workflow dedicado, com credencial mínima e policy gate.
- Manter core, agentes e adapters sem abrir PR, alterar proteção ou fazer merge.

**Promotion rule:** sem evidência suficiente, a capacidade permanece em `observed`, `replay`, `shadow` ou fallback determinístico; não é promovida para `active`.

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Tratar os nove itens como programa de evolução, não como uma mega-feature. | Reduz acoplamento e permite gates independentes. | Implementar todos os itens em uma única fatia end-to-end. |
| 2 | Medição, Evidence Coverage e segurança precedem aprendizado. | Sem ground truth e holdouts, otimização pode reforçar uma rota ruim. | Bandit ou aprendizado online desde o primeiro ciclo. |
| 3 | Adapters reais começam read-only, observados e opt-in. | Preserva a fronteira local/offline e impede claims sem receipt. | Integrar SDKs/providers no core e assumir capacidades. |
| 4 | DAG adaptativo é limitado por políticas e fallback estático. | Complexidade não pode ampliar autoridade nem remover gates. | Deixar o estimador alterar livremente a execução. |
| 5 | CLI, TUI e matriz Python consomem contratos compartilhados. | Evita duplicação de regras e compatibilidade implícita. | Modularização total como pré-requisito do runtime. |
| 6 | Governança GitHub permanece externa ao core. | Branch protection e merge dependem de credenciais, políticas e estado externo. | Aplicativo/agente mutar proteção, abrir PR ou fazer merge. |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Implementação simultânea dos nove itens | Cria uma fatia grande demais para validação, rollback e atribuição de regressões. | Yes |
| Bandit online antes de baseline e holdout confiáveis | Não há evidência externa suficiente e o risco de feedback incorreto é alto. | Yes |
| Adapters reais com claims de produção no primeiro ciclo | Capabilities, freshness, limites e falhas ainda precisam de receipts independentes. | Yes |
| DAG adaptativo sem Evidence Coverage mínima | O sistema não conseguiria explicar ou auditar a escolha da rota. | Yes |
| TUI 2.0 antes dos contratos de domínio | UX poderia cristalizar decisões ainda instáveis. | Yes |
| Branch protection mutável pelo aplicativo ou agente | Viola a separação entre core e governança externa. | No, apenas workflow/policy externo autorizado |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Roadmap order / architecture concept | ✅ | Confirmação da sequência `medição → contexto → adaptação → aprendizado → UX → governança`. | No |
| Gates and candidate requirements | ✅ | Confirmação dos gates de segurança, evidência, qualidade e reversibilidade. | No |

**Minimum Validations:** 2 concluídas

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

A primeira fatia de Intelligent Capability Routing possui contratos de roteamento e feedback, mas ainda não oferece contexto versionado, medição completa, planejamento adaptativo, otimização comprovada, adapters reais, superfícies operacionais evoluídas ou governança externa integrada; o programa deve adicionar essas capacidades em fatias independentes, auditáveis e reversíveis.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Maintainer e operador | Precisa entender por que uma rota foi escolhida, reproduzir a decisão e voltar a um fallback seguro. |
| Plataforma, DevEx e CI | Precisa consumir contratos estáveis, validar ambientes e conectar governança externa sem incorporar mutações ao core. |
| Revisor de segurança/qualidade | Precisa distinguir observação, simulação, evidência e claim de runtime ou produção. |

### Success Criteria (Draft)

- [ ] Cada onda possui contratos, dependências, owner, entry gate, exit gate e fallback explícitos.
- [ ] Uma decisão de routing pode ser reconstruída a partir de trace, policy, versão de Knowledge Pack, freshness e resultado de avaliação.
- [ ] O sistema pode comparar plano estático e adaptativo com os mesmos fixtures, golden, holdout e mutation checks.
- [ ] Adapters de providers/modelos e GitHub emitem receipts e não mutam estado externo fora do workflow/policy autorizado.
- [ ] Pesos aprendidos só podem ser promovidos após avaliação independente e possibilidade de rollback.
- [ ] CLI, TUI e matriz Python reutilizam contratos compartilhados e declaram compatibilidade observada.
- [ ] Gaps sem evidência externa permanecem registrados como `unresolved` e não viram claims de capacidade.

### Constraints Identified

- Segurança, evidência e reversibilidade têm prioridade sobre autonomia e velocidade.
- A execução local deve continuar determinística e offline-first sempre que não houver adapter/policy explícito.
- Providers, GitHub, branch protection, CI e produção permanecem fronteiras externas.
- Estimador, DAG e otimização devem respeitar budgets, timeouts, allowlists e fallback.
- A ausência de telemetria, freshness, provider capability ou política externa verificável deve bloquear promoção, não ser preenchida por memória do modelo.

### Out of Scope (Confirmed)

- Implementar os nove itens neste brainstorm; este artefato captura o roadmap e prepara a definição.
- Promover bandit ou aprendizado online sem baseline, holdout, mutation check, safety gate e rollback.
- Executar providers/modelos reais ou declarar capacidades de produção sem adapter, receipt e policy explícitos.
- Fazer o core, um agente ou um adapter alterar branch protection, abrir PR ou fazer merge.
- Tratar Knowledge Pack fresco como automaticamente correto ou suficiente.
- Declarar suporte na matriz Python apenas por configuração, sem execução e evidência do ambiente.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 4 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 2 |
| Duration | Não cronometrada |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md`
