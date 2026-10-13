# BRAINSTORM: API Forge Platform Completion

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_PLATFORM_COMPLETION |
| **Date** | 2026-09-22 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:** Corrigir todos os gaps identificados na análise crítica da API Forge e depois consolidar uma plataforma completa para engenharia de software, incluindo Git, CI/CD, IDE, interface visual, integrações externas, documentação detalhada, skills e agents preparados.

**Context Gathered:**
- O repositório possui um núcleo determinístico, contratos versionados, regras, políticas, sandbox, evidências, SDD, Graphify, adapters e perfis de agents.
- A autoanálise atual está bloqueada por uma falha não governada no extrator FastAPI, e o fluxo público `analyze -> next-step` possui incompatibilidade entre o formato gerado e o formato consumido.
- A visão atual é ampla, mas a experiência deve ser produzida por agents capazes de entender necessidades, sugerir boas práticas, comparar técnicas e arquiteturas e declarar incertezas; não será priorizado um wizard de experiência guiada.
- A plataforma deverá cobrir verticais independentes, usando projetos de exemplo para APIs, bancos, mensageria, CI/CD, cloud e front-end.
- O caso persistido `case:c1491f3c79f436f0` foi carregado e sua receipt foi verificada; ele representa uma fixture de FastAPI e não substitui a avaliação completa do produto.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/`, `agents/`, `docs/contracts/`, `docs/sdd/`, `tests/`, `.claude/sdd/features/` | Corrections must preserve the deterministic core and add vertical contracts/adapters instead of duplicating policy logic. |
| Relevant KB Domains | `genai`, `prompt-engineering`, `python`, `pydantic`, `testing`, `terraform`, `cloud-platforms`, plus project API Forge knowledge packs | Agents, structured outputs, validation, test strategy and external integration patterns need grounded guidance. |
| IaC Patterns | Terraform and SAM adapters exist; external cloud actions are adapter-owned and policy-gated | Cloud support must distinguish static/fixture/live-read-only/live-mutation evidence and never promote mutation implicitly. |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual é o objetivo principal desta fase? | Corrigir primeiro todos os gaps de confiabilidade e governança; depois construir a experiência da plataforma. | O núcleo confiável é um pré-requisito para qualquer expansão e deve bloquear a fase de produto quando seus fluxos principais falharem. |
| 2 | Que perfil deve receber a primeira experiência guiada? | A experiência guiada foi rejeitada como foco. Os agents devem adaptar a atuação à necessidade do usuário, sugerir boas práticas e explicar técnicas e arquiteturas. | O investimento passa de wizard/persona-flow para qualidade de agents, skills, documentação, perguntas de esclarecimento e recomendações justificadas. |
| 3 | Qual o escopo de “todos os gaps”? | Absolutamente tudo, incluindo Git, CI/CD, IDE, interface visual e integrações externas. | O escopo estratégico inclui toda a plataforma, mas a implementação deve ser vertical, sequenciada e comprovada para evitar acoplamento e promessas sem evidência. |
| 4 | Que amostras devem validar a plataforma? | Projetos de exemplo cobrindo APIs, bancos, mensageria, CI/CD, cloud e front-end. | Será necessária uma matriz de fixtures com casos positivos, negativos, incompletos e ambíguos, além de ground truth revisado para recomendações dos agents. |

**Minimum Questions:** 4 (to ensure clarity before proceeding)

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | A criar em fixtures por vertical: APIs, bancos, mensageria, CI/CD, cloud e front-end | TBD | Devem incluir código, contratos, configuração, manifests, pipelines e sinais incompletos quando aplicável. |
| Output examples | A criar em casos golden por vertical | TBD | Devem conter recomendação, alternativas, evidências, incertezas, riscos e próximo verificador. |
| Ground truth | A criar por revisão humana e por especialistas de domínio | TBD | Deve registrar a decisão esperada, os fatos que a sustentam e as recomendações aceitáveis. |
| Related code | `src/apiforge/`, `agents/`, `docs/contracts/`, `docs/sdd/`, `tests/` | Existente | Reutilizar contratos, policies, evidence receipts, TaskSpec, adapters e padrões de teste existentes. |

**How samples will be used:**

- Validar que cada agent identifica corretamente a necessidade antes de recomendar uma solução.
- Servir como referência few-shot e como contrato de saída estruturada.
- Testar casos conhecidos, ambiguidades, ausência de evidência e recomendações conflitantes.
- Alimentar golden, holdout e mutation checks para impedir regressões silenciosas.
- Comprovar paridade entre CLI, MCP, IDE e interface visual sobre os mesmos fatos e contratos.

---

## Approaches Explored

### Approach A: Núcleo confiável + plataforma por verticais ⭐ Recommended

**Description:** Corrigir o núcleo, estabilizar contratos e capabilities e, em seguida, entregar Git, CI/CD, IDE, UI, cloud, APIs, bancos, mensageria e front-end como verticais independentes. Cada vertical terá adapter, skill, agent, documentação, fixtures, testes, contrato, evidências e rollback.

**Pros:**
- Preserva a modularidade atual do núcleo determinístico.
- Permite provar cada capacidade separadamente.
- Facilita rollback, evolução e suporte a diferentes superfícies.
- Mantém mutações externas atrás de adapters, policies e aprovação.

**Cons:**
- Requer disciplina de contratos e uma sequência de implementação mais longa.
- A cobertura total aparecerá gradualmente, não em uma entrega monolítica.

**Why Recommended:** Há correspondência forte com a separação já existente em `src/apiforge/`, `agents/`, `docs/contracts/` e `docs/sdd/`. Os domínios `genai`, `testing`, `python`, `pydantic`, `terraform` e `cloud-platforms` da KB apoiam a divisão entre agentes, validação, contratos e integrações. **Confidence: 0.95.**

---

### Approach B: Suíte monolítica “tudo em um”

**Description:** Construir uma experiência única que coordene código, cloud, banco, CI/CD, IDE, interface visual e integrações desde o início.

**Pros:**
- Visão unificada para o usuário final.
- Pode parecer simples quando o fluxo é totalmente feliz.

**Cons:**
- Alto acoplamento entre interfaces, adapters e políticas.
- Falhas em uma integração contaminam o fluxo inteiro.
- Torna testes, rollback e suporte mais difíceis.

**Why not recommended:** A estrutura atual é modular e a própria análise revelou que o caminho principal ainda possui falhas de integração. Um monólito aumentaria a superfície antes de estabilizar o contrato central. **Confidence: 0.80.**

---

### Approach C: Orquestrador fino sobre ferramentas externas

**Description:** Manter o API Forge como camada de decisão, evidência e governança, delegando execução a Git, IDEs, CI/CD, scanners, provedores cloud, bancos e ferramentas de mensageria.

**Pros:**
- Amplia cobertura com menos implementação proprietária.
- Aproveita ferramentas maduras do ecossistema.
- Combina com o desenho offline-first e com adapters já existentes.

**Cons:**
- Depende de versões, credenciais, disponibilidade e contratos externos.
- Pode gerar grande variabilidade entre ambientes.
- Exige uma camada forte de capability detection e refusal handling.

**Why not recommended as the primary approach:** Deve ser usado dentro das verticais da Abordagem A, não como substituto do núcleo. Sem contracts, evidence e policies estáveis, o orquestrador apenas espalharia a complexidade para fora. **Confidence: 0.85.**

---

## Data Engineering Context (if applicable)

> Include this section when the feature involves data pipelines, ETL, analytics, or data infrastructure.

### Source Systems

| Source | Type | Volume Estimate | Current Freshness |
|--------|------|-----------------|-------------------|
| Fixtures de APIs | Código/contratos | Unknown | Versionada no repositório |
| Fixtures de bancos | Código, schemas e manifests | Unknown | A definir |
| Fixtures de mensageria | Código, tópicos, filas e políticas | Unknown | A definir |
| Fixtures de cloud | IaC e dumps offline | Unknown | A definir |
| Fixtures de CI/CD | Pipelines e reports | Unknown | A definir |
| Fixtures de front-end | Código, builds e contratos de integração | Unknown | A definir |

### Data Flow Sketch

```text
[Projeto de exemplo]
        -> [inventário determinístico]
        -> [facts + contratos + sinais]
        -> [agent especializado]
        -> [recomendações + alternativas + unresolved]
        -> [plano governado]
        -> [sandbox / adapter / verificador]
        -> [evidência + Outcome Brief]
```

### Key Data Questions Explored

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual volume real deve ser suportado? | Ainda não definido. | Deve ser medido por fixtures e projetos reais antes de prometer capacidade. |
| 2 | Qual frescura é necessária? | Offline-first para o núcleo; leituras externas dependem de adapters e políticas. | Runtime claims, cloud posture e integrações precisam declarar idade e origem da evidência. |
| 3 | Quem consome a saída? | Engenheiros de software, agents, CI/CD, IDE e interface visual. | Os contratos devem ser comuns, mas as apresentações podem ser específicas por superfície. |

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-09-22, confirmado na sessão de brainstorm |
| **Reasoning** | Corrigir o núcleo primeiro e ampliar por verticais independentes preserva a confiabilidade, permite validar cada integração e mantém todos os domínios no escopo estratégico sem exigir uma entrega monolítica. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|---------------------|
| 1 | O núcleo determinístico é bloqueador da expansão. | Agents e integrações não devem mascarar falhas de facts, contracts, evidence ou policy. | Expandir capabilities antes de corrigir `discover`, `index` e `next-step`. |
| 2 | A plataforma será entregue por verticais independentes. | Cada domínio precisa de contrato, adapter, skill, agent, fixture, teste e rollback próprios. | Suíte monolítica “tudo em um”. |
| 3 | Agents adaptam sua atuação à necessidade do usuário. | O valor está em entendimento contextual, boas práticas e trade-offs justificados. | Wizard fixo ou experiência guiada baseada somente em persona. |
| 4 | Todas as integrações permanecem no escopo estratégico. | Git, CI/CD, IDE, UI, cloud, APIs, dados, mensageria e front-end fazem parte da visão final. | Remover integrações da visão do produto. |
| 5 | Ações externas continuam governadas. | Segurança e reversibilidade exigem adapter explícito, policy, aprovação e evidência. | Mutação automática ou direta a partir de uma recomendação textual. |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Experiência guiada como produto principal | O usuário pediu agents adaptativos e documentação detalhada, não um wizard obrigatório. | No — substituída por orientação contextual dos agents. |
| Entrega simultânea de todas as integrações no primeiro MVP | Aumentaria acoplamento e impediria provar o núcleo; as integrações continuam na visão de longo prazo. | Yes — por verticais e após os contratos centrais. |
| Ações externas diretas sem aprovação | Viola a governança, o modelo offline-first e a necessidade de rollback. | No — apenas adapters governados poderão executar ações autorizadas. |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | Confirmado. Núcleo confiável, contracts/capabilities, agents adaptativos, verticais e superfícies compartilhadas. | No |
| Component breakdown | ✅ | Confirmado. Core, orchestration, knowledge, adapters, verification lab, delivery surfaces e integration gateway. | No |
| Data flow | ✅ | Confirmado implicitamente pela escolha de fixtures por vertical e agents orientados a evidências. | No |
| Error handling | ✅ | A estratégia deve preservar `unresolved`, refusal codes, evidências e próximo verificador, sem tracebacks não governados. | No |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

A API Forge possui uma base determinística e auditável, mas ainda apresenta gaps de confiabilidade, contratos de CLI, cobertura de integração, documentação e preparação de agents que impedem seu uso como plataforma abrangente de engenharia de software.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Engenheiro iniciante | Precisa de recomendações explicadas, práticas seguras e documentação que não dependa de conhecimento prévio sobre todos os conceitos do sistema. |
| Engenheiro intermediário | Precisa analisar, construir, testar e evoluir APIs, dados, mensageria e pipelines com orientação contextual. |
| Engenheiro especialista | Precisa de governança, evidências, arquitetura comparada, automação controlada e integração com ferramentas reais. |
| Maintainer de plataforma | Precisa de contracts, capability matrix, fixtures, testes, release evidence e compatibilidade entre CLI, MCP, IDE e UI. |

### Success Criteria (Draft)

- [ ] Os fluxos principais da CLI e do MCP não produzem traceback para entradas suportadas ou situações explicitamente `unresolved`.
- [ ] `analyze -> next-step -> graph -> evidence -> brief` funciona com o formato oficial dos artefatos.
- [ ] A autoanálise do próprio repositório produz facts, findings e gaps governados, sem falha não classificada.
- [ ] Cada capability declara suporte, limitações, evidência, pré-requisitos, risco e rollback.
- [ ] Cada vertical possui fixtures, casos golden, holdouts, mutation checks, documentação e um agent/skill correspondente.
- [ ] Agents entendem a necessidade, fazem perguntas quando necessário, recomendam alternativas e citam evidências sem inventar fatos.
- [ ] CLI, MCP, IDE e interface visual usam os mesmos contracts e não divergem em decisões.
- [ ] Git, CI/CD, cloud, bancos, mensageria e ferramentas externas operam somente por adapters governados.
- [ ] A documentação permite instalar, executar, interpretar, verificar e recuperar cada fluxo suportado.
- [ ] SDD, release evidence, lint, type checking, testes e manifests refletem o estado atual do repositório.

### Constraints Identified

- O núcleo permanece offline-first, determinístico e sem dependência de SDKs de modelos.
- Ações cloud, database, broker, Git e CI/CD devem passar por adapters explícitos e gates de policy.
- Nenhum fato, versão, custo, throughput, permissão ou capability pode ser inventado.
- `unresolved`, `refused`, `not_observed`, `inconclusive` e `confirmed` devem permanecer distintos.
- Alterações geradas devem passar por sandbox, branch/worktree e verificação independente.
- A expansão deve manter compatibilidade entre contratos, CLI, dispatch, MCP, skills, agents e host mirrors.
- O escopo é amplo, mas a entrega será sequenciada por dependências e evidência.

### Out of Scope (Confirmed)

- Wizard obrigatório ou experiência guiada como mecanismo principal de uso.
- Mutação externa automática sem policy, aprovação, evidência e rollback.
- Declarar suporte de produção apenas porque existe um parser, um agent ou uma integração nominal.
- Expandir especializações antes de corrigir os gaps críticos do núcleo e do fluxo de artefatos.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 4 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 3 |
| Validations Completed | 2 |
| Duration | Single collaborative session |

---

## Shipment Record

Shipped and archived on 2026-09-22.
