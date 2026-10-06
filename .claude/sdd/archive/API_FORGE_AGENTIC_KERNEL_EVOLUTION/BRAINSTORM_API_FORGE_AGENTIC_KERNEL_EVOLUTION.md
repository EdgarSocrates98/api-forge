# BRAINSTORM: API Forge Agentic Kernel Evolution

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_KERNEL_EVOLUTION |
| **Date** | 2026-09-23 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Shipped |

---

## Initial Idea

**Raw Input:**

> Quero fazer o máximo possível para atender todas as indicações de melhorias e evoluções do projeto citadas em `prompt_evo_avalicao_evolucao.md`, trabalhando ao máximo para conseguirmos fazer tudo que traga melhoria e evolução para o projeto. O Docker Desktop está ligado para uso, se necessário.

**Context Gathered:**

- O projeto já possui um núcleo determinístico com TaskSpec, policy, evidências, sandbox, verificador, autonomia, capabilities, evals e SDD.
- O caso persistido em `.apiforge/case/` foi carregado antes da análise; o snapshot contém `api-ir.json`, `facts.json`, `findings.json`, `case.json` e `receipt.json`.
- `runtime/control.py` já implementa dependências, leases, retry, cancelamento, review e replay; `runtime/scheduler.py` implementa fan-out limitado.
- O supervisor principal ainda cria invocações sem dependências, e `resume` reexecuta a tarefa em vez de retomar um estado persistido de forma idempotente.
- `autonomy/heal.py` detecta divergência de hash no rollback, mas ainda segue para a escrita; isso precisa virar conflito nomeado e preservado.
- `capabilities/registry.py` e `capability_matrix.yaml` fornecem uma matriz pública estática; falta um perfil de capability de agent e um scorecard histórico governado por evals.
- `evals/suite.py` já fornece casos declarativos, holdout e mutation digest, mas precisa evoluir para falhas de autonomia, tool-use, colaboração e outcome.
- A experiência de entrada é complexa; a CLI deve receber uma fachada intent-driven sem mover regras de negócio para a camada de apresentação.
- As restrições do projeto permanecem: offline-first, sandbox, read-only externo, aprovação explícita para mutação, evidência preservada e compatibilidade versionada.
- O comando `next-step` foi executado antes de escolher qualquer rota; como o snapshot anterior não tinha findings, ele retornou a recusa nomeada `AF-ROUTING-NO-FINDINGS`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/runtime`, `src/apiforge/contracts`, `src/apiforge/autonomy`, `src/apiforge/capabilities`, `src/apiforge/evals`, serviços de aplicação e CLI | O kernel deve ser evoluído por contratos e serviços, com uma única autoridade de estado |
| Relevant KB Domains | `genai`, `python`, `testing`, `pydantic`, `component-model` | Usar state machines, workflow plan-and-execute, clean architecture, contratos tipados, evals e separação agent/skill/command/KB |
| IaC Patterns | Não aplicável ao kernel; CI e adapters locais já existem | Docker permanece opcional para provas de integração, sem ampliar autoridade de mutação |

**Evidence and confidence basis:**

- `genai` state machines, agentic workflow and evaluation framework + matching runtime/control-plane code: strong recommendation, confidence 0.95.
- `python` clean architecture + existing modular package and ports-like adapters: strong recommendation with incremental migration, confidence 0.90.
- `testing` unit/integration patterns + existing runtime/autonomy tests and fixtures: strong validation basis, confidence 0.90.
- Capability profiles and scorecards have a codebase foundation but require new contracts and measurements: adaptation required, confidence 0.85.

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual é o objetivo principal deste ciclo? | Executar uma evolução ampla por fases e, no ciclo inicial, entregar código começando pelo runtime/autonomia, self-healing e verificação. | O programa será amplo, mas cada fatia deverá entregar implementação verificável, não apenas roadmap. |
| 2 | Quem deve ser o usuário prioritário? | Desenvolvedor/arquiteto de APIs como porta de entrada e equipe de plataforma/governança como base obrigatória. | A DX será progressive disclosure; a governança permanecerá canônica e não poderá ser contornada pela CLI. |
| 3 | Quais restrições são inegociáveis? | Preservar offline-first, sandbox, read-only externo, evidências e gates; preservar compatibilidade da CLI e dos artefatos; mudanças incompatíveis exigem migração explícita e registro. | A implementação será aditiva sempre que possível, com adaptadores de leitura e migrações nomeadas. |
| 4 | Como medir o sucesso? | Provar runtime resiliente, qualidade/evals e experiência de uso; o ciclo não fecha se qualquer uma das três dimensões ficar sem evidência. | Cada fatia terá testes de kernel, eval gate e uma projeção DX correspondente. |

**Minimum Questions:** 3 (to ensure clarity before proceeding)

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `prompt_evo_avalicao_evolucao.md`, `.apiforge/case/`, TaskSpec fixtures, runtime/autonomy fixtures | Available local set | O documento de avaliação é a fonte das recomendações; o caso e as fixtures são entradas reprodutíveis. |
| Output examples | `.apiforge/case/`, `.apiforge/tasks/` quando presentes, `RunStore` artifacts, reports SDD arquivados | Available local set | Servem como formato existente para runs, receipts, replay, briefs e relatórios. |
| Ground truth | Testes de `runtime`, `autonomy`, `sdd`, `capabilities`, `evals`, `labs` e SDDs shipped | Available local set | Testes e gates existentes definem comportamento aceito; cenários de falha serão adicionados como holdout/adversarial. |
| Related code | `src/apiforge/runtime`, `src/apiforge/autonomy`, `src/apiforge/contracts`, `src/apiforge/capabilities`, `src/apiforge/evals`, `src/apiforge/cli.py` | Available local set | Reutilizar contratos, policy, ledger, control plane, adapters e renderização existentes. |

**How samples will be used:**

- Regressão de comportamento da CLI e dos artefatos existentes.
- Golden tests para transições do runtime, recuperação de lease, retry, cancelamento, replay e verificação.
- Holdout/mutation para garantir que falhas de autonomia não sejam aceitas como sucesso.
- Casos de concorrência para validar rollback sem sobrescrever alterações externas.
- Validação de que toda afirmação continua ligada a evidência, gaps e limitações.

---

## Approaches Explored

### Approach A: Kernel-first incremental ⭐ Recommended

**Description:** Unificar `ControlPlane`, `scheduler` e `supervisor`; endurecer self-healing; adicionar profiles/scorecards e evals; entregar uma fachada DX no final de cada fatia.

**Pros:**

- Ataca a lacuna arquitetural mais relevante sem abandonar a base existente.
- Mantém política, evidência, replay e verificação no centro.
- Permite provar cada mudança com testes, holdouts e uma projeção de uso.

**Cons:**

- A primeira entrega concentra mais trabalho interno antes de uma UX completa.
- Exige migração coordenada de contratos, persistência, runtime e testes.

**Why Recommended:** O KB `genai` recomenda state machines e workflow plan-and-execute com edges controladas pelo runtime; isso corresponde ao `ControlPlane` existente e evita criar um segundo orchestrator. A confiança é 0.95 porque há padrão de KB e correspondência direta no código.

---

### Approach B: DX-first facade

**Description:** Criar primeiro `review`, `doctor`, `status`, `resume`, `evolve` e demais verbos intent-driven sobre o runtime atual; endurecer o kernel conforme os casos de uso surgirem.

**Pros:**

- Entrega valor visível rapidamente para desenvolvedores.
- Expõe cedo os pontos de fricção da experiência.

**Cons:**

- Pode criar uma segunda camada de orquestração e outra fonte de estado.
- A CLI pode esconder limitações de resume, idempotência e verificação.

**Why not recommended:** A dívida seria deslocada para a superfície de entrada enquanto o problema de autoridade entre `ControlPlane` e supervisor permaneceria.

---

### Approach C: Evals/Knowledge-first

**Description:** Transformar evals, knowledge packs, freshness, evidence levels e scorecards no primeiro produto, governando as futuras mudanças do runtime.

**Pros:**

- Aumenta a densidade real dos especialistas.
- Reduz risco de declarar autonomia com base apenas em respostas convincentes.

**Cons:**

- Entrega pouco valor visível antes de melhorar o runtime.
- Exige modelagem de dados e versionamento antes da integração operacional.

**Why not recommended:** A suíte de evals atual é uma boa fundação, mas sem corrigir retomada, idempotência e rollback ela não prova autonomia operacional completa.

---

## Data Engineering Context (if applicable)

Não aplicável ao núcleo desta feature. Adapters de dados, messaging e analytics permanecem especializados e read-only; não haverá generalização de engine nem inferência de runtime externo.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — Kernel-first incremental |
| **User Confirmation** | 2026-09-23 |
| **Reasoning** | O usuário confirmou A, incorporando entregas DX da B no final de cada fatia e usando C como gate de qualidade. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | `ControlPlane` será a autoridade do ciclo de vida do runtime | Já possui estado, dependências, leases, retry, cancelamento, review e replay; unificação reduz fontes concorrentes | Manter `supervisor` e `ControlPlane` como runtimes paralelos |
| 2 | O runtime valida o DAG proposto antes da execução | O modelo pode propor; política e runtime autorizam | Orchestrator LLM com autoridade sobre fluxo |
| 3 | Rollback concorrente será fail-safe | Alteração externa deve virar conflito preservado, não sobrescrita | Restaurar snapshot após apenas registrar divergência |
| 4 | Evals serão gates de cada fatia | Outcome, holdout e cenários de falha comprovam comportamento operacional | Aceitar respostas ou smoke tests como prova suficiente |
| 5 | A DX será uma projeção do kernel | Mantém CLI, MCP, IDE e UI semanticamente alinhados | Colocar regras de negócio em cada superfície |
| 6 | A evolução será modular monolith com ports/adapters | Preserva offline-first e facilita hosts/provedores futuros | Microservices ou dependência direta de SDKs no domínio |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| TUI completa | Não é necessária para provar o kernel; a CLI projetada cobre a primeira DX | Yes |
| Web UI | Amplia superfície e não resolve a autoridade do runtime | Yes |
| Knowledge packs com atualização externa automática | Freshness e autoridade exigem adapters e receipts próprios | Yes |
| Host capability negotiation completa | Depende de capabilities reais por host; não deve ser simulada | Yes |
| Matriz imediata para versões futuras do Python | A compatibilidade não resolve as lacunas centrais de autonomia | Yes |
| Proteção remota da branch, CODEOWNERS e regras do GitHub | É mutação externa fora do sandbox e exige ação humana/repositório | Yes, via workflow governado |
| Integrações externas mutáveis | O core permanece read-only; mutation exige adapter, gate, rollback e receipt | Yes, outside local core |
| Novos agents em grande volume | A prioridade é densidade de capability, evals e ferramentas dos agents existentes | Yes, only when justified by evidence |
| Microservices | O projeto ainda se beneficia mais de modular monolith e contratos locais | Revisit later |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | Aprovado | No |
| Component breakdown | ✅ | Aprovado | No |
| Scope and YAGNI | ✅ | Aprovado | No |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

O API Forge possui componentes fortes para execução agêntica, mas o runtime principal ainda não transforma de maneira única e comprovável DAG, retomada, leases, retry, cancelamento, idempotência, rollback concorrente, capability routing, evals e DX em um fluxo operacional integrado.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Desenvolvedor/arquiteto de APIs | Precisa de uma entrada simples para revisar, evoluir e recuperar uma execução sem conhecer todos os comandos internos. |
| Equipe de plataforma e governança | Precisa provar quais capabilities estão disponíveis, sob quais evidências, riscos, limitações e histórico de qualidade. |

### Success Criteria (Draft)

- [ ] O runtime executa TaskSpecs com DAG persistido, dependências validadas, leases, retry, checkpoint, cancelamento, resume e idempotência, com replay verificável.
- [ ] Self-healing nunca sobrescreve alteração concorrente; conflitos são preservados como estado nomeado e entram nos gaps/evidências.
- [ ] Cada fatia possui evals golden, holdout, mutation e cenários de falha apropriados, com verificação independente e outcome observável.
- [ ] Capability routing considera requisitos, evidência, risco, limitações e scorecard; ausência de prova permanece `unresolved`.
- [ ] A CLI oferece progressivamente `doctor`, `status`, `review`, `evolve` e `resume` sem duplicar regras do kernel.
- [ ] CLI, MCP, IDE e UI projetam os mesmos contratos e estados, preservando compatibilidade dos artefatos existentes.

### Constraints Identified

- Offline-first e sem SDK de modelo no core.
- Adapters externos read-only; mutação requer boundary, policy, approval, rollback, receipt e verificação independente.
- Sem escrita direta na main tree durante build; usar sandbox, branch ou worktree governado.
- Preservar `unresolved`, códigos `AF-*`, hashes, fatos, findings, receipts e limitações.
- Compatibilidade aditiva ou migração explícita para CLI, contratos e artefatos.
- Docker é opcional e só pode ser usado em provas permitidas; não amplia claims para produção.

### Out of Scope (Confirmed)

- Web UI e TUI completa neste primeiro programa.
- Mutation de GitHub, AWS, bancos, brokers ou provedores externos.
- Suposta equivalência entre capabilities de hosts sem evidência do host.
- Criação massiva de agents ou migração para microservices.
- Declaração de produção verificada a partir de fixtures locais.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | quatro perguntas de descoberta e uma pergunta de amostras |
| Approaches Explored | três |
| Features Removed (YAGNI) | vários itens de superfície, integração externa e expansão prematura |
| Validations Completed | arquitetura, componentes e escopo |
| Duration | uma sessão |

---

## Ship Revision

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-09-23 | ship-agent | Archived with the completed DEFINE, DESIGN and BUILD artifacts |

## Next Step

**Archived:** feature shipped on 2026-09-23; use the archived DEFINE/DESIGN/BUILD artifacts as the historical source of truth.
