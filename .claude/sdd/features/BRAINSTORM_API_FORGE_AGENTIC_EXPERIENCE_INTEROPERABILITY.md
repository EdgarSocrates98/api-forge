# BRAINSTORM: API Forge Agentic Experience and Interoperability

> Evolução UX-first do API Forge para TUI, evidência completa, conhecimento fresco, interoperabilidade de hosts, cobertura Python, CLI modular e debate adaptativo.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY |
| **Date** | 2026-09-23 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:**

> Agora vamos planejar e fazer os itens adiados da evolução anterior: TUI completa; Knowledge Packs com atualização/freshness externa; negociação real de capabilities entre Codex, Claude, Devin e Copilot; matriz oficial para Python além da versão atual; refatoração total da CLI em todos os submódulos; Evidence Levels completos em todos os contratos; e debate adaptativo avançado com múltiplos modelos. A UX/TUI deve ser prioridade, sem deixar as outras opções de fora.

**Context Gathered:**

- O kernel determinístico já possui `RuntimeExperience`, `ControlPlane`, scheduler, supervisor, `RunStore`, replay, eval gate e CLI friendly; a TUI deve projetar esses serviços, não substituí-los.
- O repositório já possui adapters read-only para receipts externos e freshness, loader fechado de Knowledge Packs, `EvidenceLevel` em contratos de adapter e agentes de host para Claude, GPT/Codex, Devin e Copilot.
- A paridade atual é declarativa e honesta: hosts não são equivalentes sem prova; freshness externa não é inferida de fixtures; e o debate existente deve evoluir com budget, risco, dissent e replay.
- A matriz Python e o suporte de versões precisam ser publicados apenas a partir de execução observada; a versão atual não será extrapolada silenciosamente para outras versões.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/application`, `src/apiforge/contracts`, novo `src/apiforge/tui`, `src/apiforge/knowledge`, `src/apiforge/agentops`, `src/apiforge/debate` | A TUI e os novos contratos devem consumir o core por facades e adapters governados |
| Relevant KB Domains | `genai`, `python`, `testing`, `prompt-engineering`, `data-quality` | Usar state machines, guardrails, schemas versionados, fixtures, snapshots e freshness explícita |
| Existing Patterns | `RuntimeExperience`, `EvidenceLevel`, `knowledge/loader.py`, `integrations/external.py`, `agentops/hosts.py`, `agentops/parity.py`, Typer CLI | Evoluir contratos aditivamente e preservar CLI/JSON expert |
| IaC Patterns | Não aplicável à primeira fatia; Docker é opcional | TUI e validações devem funcionar offline no workspace |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual objetivo deve guiar a primeira fatia: UX, confiança, interoperabilidade ou cobertura técnica? | **UX — TUI**, sem retirar as demais frentes | A TUI é o primeiro valor visível; todas as outras frentes entram no roadmap e serão integradas por fatias verticais |
| 2 | Qual fluxo deve ser o núcleo da TUI? | **Ambos**: execução do desenvolvedor e governança, com execução como tela inicial | A navegação precisa cobrir runs, resume, review, doctor, evidências, gaps, capabilities e debates |
| 3 | Qual restrição técnica deve orientar a TUI? | **Textual/Rich + compatibilidade progressiva** | A experiência principal usará camada terminal dedicada, com fallback Rich/CLI/JSON quando TUI ou runtime visual não estiver disponível |
| 4 | Quais amostras devem fundamentar as validações? | Artefatos existentes mais cenários sintéticos para TUI, freshness, negociação e debates | Fixtures reais preservam contratos atuais; cenários sintéticos cobrem estados e falhas ainda ausentes |

**Minimum Questions:** 4 (to ensure clarity before proceeding)

---

## Sample Data Inventory

> Os samples serão usados como ground truth local; nenhuma amostra externa será tratada como prova de produção sem receipt verificável.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/agentic_runtime/kernel_scenarios.yaml`, `tests/evals/cases/kernel_evolution.yaml` | 2 | Cenários de runtime, timeout, schema, tool refusal, conflict, golden, holdout e mutation |
| Output examples | `tests/application/test_runtime_experience.py`, `tests/e2e/test_governance_cli.py`, `tests/e2e/test_agentic_slice.py` | 3 módulos | Payloads canônicos de status, review, resume, gaps, evidence e CLI parity |
| Ground truth | `src/apiforge/runtime/control.py`, `src/apiforge/runtime/store.py`, `src/apiforge/runtime/supervisor.py` | 3 componentes | Fonte de verdade para transições, persistência, replay, leases e idempotência |
| Evidence samples | `src/apiforge/contracts/adapter.py`, `src/apiforge/contracts/integration.py`, `src/apiforge/integrations/external.py` | 3 componentes | Evidence levels, receipts, hash, observed_at e freshness window |
| Host samples | `src/apiforge/agentops/hosts.py`, `src/apiforge/agentops/parity.py`, `src/apiforge/agentops/activation.py` | 3 componentes | Declarations, diferenças de host e activation plan |
| Knowledge samples | `knowledge/`, `src/apiforge/knowledge/loader.py`, `tests/knowledge/test_packs.py` | Pack tree + loader + tests | Schema fechado, source authority, runtime matrix e evals |

**How samples will be used:**

- Snapshots e testes de contrato para assegurar que TUI, Rich, CLI e JSON projetam os mesmos estados.
- Fixtures sintéticas para estados vazios, stale, unresolved, divergência, debate sem quorum e capability ausente.
- Testes de compatibilidade aditiva para que runs, artifacts e contracts atuais permaneçam legíveis.
- Golden/holdout/mutation para impedir que freshness, host parity ou debate sejam aceitos sem prova.

---

## Approaches Explored

### Approach A: UX-first em fatias verticais ⭐ Recommended

**Description:** Construir a TUI primeiro sobre os serviços canônicos e, ao final de cada fatia, expor a capacidade na TUI, CLI e JSON. A sequência é: TUI shell e navegação; Evidence Levels; Knowledge Packs/freshness; host capability negotiation; matriz Python; modularização da CLI; debate adaptativo multi-modelo.

**Pros:**

- Entrega valor visível cedo para desenvolvedores e governança.
- Obriga cada capacidade nova a possuir uma projeção operacional coerente.
- Mantém o ControlPlane, policy, evidence e verifier como autoridades únicas.
- Permite usar Textual/Rich com fallback progressivo e testes offline.

**Cons:**

- A TUI inicial expõe lacunas de contratos que precisarão ser resolvidas nas fatias seguintes.
- A compatibilidade visual e de terminal exige snapshots e uma disciplina de projection models.

**Why Recommended:** O código já possui `RuntimeExperience`, control state, replay e CLI canônica. O ganho de UX pode ser entregue sem esperar todas as integrações, enquanto as demais frentes permanecem planejadas e entram por contratos aditivos. Confidence: **0.95**, por correspondência direta com os patterns existentes.

---

### Approach B: Contratos primeiro

**Description:** Definir Evidence Levels, Host Capability Matrix, Knowledge Freshness e Debate IR antes de construir a TUI.

**Pros:**

- Reduz risco semântico e retrabalho entre as sete frentes.
- Facilita compatibilidade entre TUI, CLI, MCP e adapters.

**Cons:**

- Adia a primeira entrega visível.
- Pode produzir contratos especulativos antes de observar os fluxos reais de uso.

---

### Approach C: Trilhas paralelas

**Description:** Implementar TUI, knowledge, hosts, Python, CLI, evidence e debate em paralelo, com integração posterior.

**Pros:**

- Maior cobertura aparente em menor tempo de calendário.

**Cons:**

- Aumenta conflitos de contratos e integração.
- Torna mais difícil atribuir falhas de eval ou regressões a uma fatia específica.
- Pode gerar superfícies que não compartilham a mesma semântica do kernel.

---

## Data Engineering Context (if applicable)

Não aplicável como pipeline de dados. Knowledge Packs e receipts externos são tratados como artefatos versionados e observações read-only, não como ETL ou armazenamento externo mutável.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A — UX-first em fatias verticais |
| **User Confirmation** | 2026-09-23 |
| **Reasoning** | O usuário confirmou TUI como prioridade, com execução e governança na mesma experiência, sem deixar nenhuma das outras seis frentes fora do programa |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | TUI é uma projeção do core | Evita semântica divergente e preserva CLI/MCP/JSON | TUI com acesso direto a stores e adapters |
| 2 | Execução e governança entram na primeira TUI | O mesmo usuário precisa acompanhar run e provar seu resultado | TUI apenas como monitor de progresso |
| 3 | Textual/Rich com fallback progressivo | Entrega UX rica sem quebrar ambientes sem suporte visual | `curses` puro como única superfície |
| 4 | Todas as sete frentes permanecem no roadmap | A prioridade é UX, não exclusão de escopo | Entregar somente a TUI e postergar indefinidamente as demais |
| 5 | Freshness, host parity e modelos externos continuam read-only e evidence-driven | O projeto não pode converter disponibilidade ou fixture em claim de produção | Inferir equivalência, freshness ou qualidade de provider |
| 6 | Debate multi-modelo começa bounded e reproduzível | Quorum, budget, dissent e replay precisam ser verificáveis | Fan-out ilimitado e consenso implícito |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Web UI pesada na primeira fase | Não é necessária para resolver a experiência terminal e aumentaria superfície de deploy | Yes |
| Mutação automática em providers externos | Viola o boundary read-only e exigiria policy/approval/receipt adicionais | Yes, only behind explicit gates |
| Equivalência automática entre hosts | Sem evidência específica, a promessa seria incorreta | Yes, per capability and receipt |
| Fan-out ilimitado de modelos no debate | Não é seguro nem reproduzível sob budget aberto | Yes, bounded adapters remain in scope |
| Matriz de versões Python baseada apenas em declaração | Não prova compatibilidade sem execução observada | Yes, after matrix runs |

As sete frentes solicitadas não foram removidas: TUI, Knowledge Packs/freshness, host negotiation, matriz Python, CLI modular, Evidence Levels e debate adaptativo continuam em escopo.

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Programa e sequência | ✅ | `Ok`; UX/TUI é primeira fatia e nenhuma frente é retirada | No |
| Componentes e fluxo | ✅ | `Ok`; TUI cobre execução e governança e usa o core canônico | No |
| Restrição técnica | ✅ | `A + C`; Textual/Rich com compatibilidade progressiva | Yes — fallback Rich/CLI/JSON incorporado |
| Amostras | ✅ | `B`; artefatos existentes mais cenários sintéticos | Yes — fixtures sintéticas incluídas no plano |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

O API Forge possui um kernel determinístico comprovável, mas seus usuários ainda precisam combinar CLI, arquivos, contratos e adapters para acompanhar execução, governança, conhecimento, host capabilities, compatibilidade e debate; falta uma experiência terminal unificada e uma base formal para essas evoluções.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Desenvolvedor de API | Não possui uma tela única para iniciar, acompanhar, revisar e retomar uma evolução com seus artifacts e gaps |
| Engenheiro de plataforma | Precisa operar Evidence Levels, freshness, capability routing e compatibilidade sem perder proveniência |
| Maintainer de hosts | Não consegue distinguir paridade declarada de capability realmente observada em cada host |
| Revisor de qualidade | Precisa de debates, dissent, score e evals reproduzíveis sem fan-out ilimitado |

### Success Criteria (Draft)

- [ ] A TUI e seus fallbacks projetam os mesmos status, gaps, evidências e códigos dos application services em todos os fluxos principais.
- [ ] Nenhuma ação da TUI escreve diretamente em stores ou integrações; mutações continuam passando por policy, ControlPlane e verifier.
- [ ] Evidence Levels são explícitos e compatíveis nos contratos relevantes; dados legados continuam carregáveis sem sucesso silencioso.
- [ ] Knowledge Packs carregam autoridade, versão, source hash, observed_at, freshness window e estado `fresh`/`stale`/`unresolved`; atualização externa é GET-only e receipt-backed.
- [ ] Host negotiation retorna capabilities por host, prerequisites, limitações e evidence refs sem declarar equivalência não comprovada.
- [ ] A matriz Python publica apenas combinações executadas em CI/local gate, com resultado, ambiente, hashes e limitações.
- [ ] A CLI é modularizada incrementalmente sem quebrar comandos expert, aliases ou payloads canônicos.
- [ ] O debate adaptativo seleciona quorum e número de participantes por risco, budget e dissent, com adapters fake/reais separados e replay determinístico.
- [ ] Cada fatia tem testes unitários, integração, snapshot/golden, holdout e mutation; `ruff check .`, mypy e SDD gates permanecem verdes.

### Constraints Identified

- Offline-first no core e sem SDK de provider/modelo importado diretamente por `src/`.
- TUI opcional, com fallback Rich/CLI/JSON para headless, CI e hosts sem suporte.
- External freshness, host negotiation e model adapters são read-only ou sandboxed até haver policy gate e receipt.
- Compatibilidade aditiva, migração explícita e preservação de `unresolved`, `AF-*`, hashes e evidências.
- Não inventar versões Python, disponibilidade de host, freshness, quorum, custo ou qualidade sem execução/receipt correspondente.
- O Docker Desktop pode apoiar provas locais, mas não transforma fixtures em claims de produção.

### Out of Scope (Confirmed)

- Web UI pesada na primeira fase.
- Mutação automática em GitHub, AWS, bancos, brokers, hosts ou providers de modelos.
- Declaração de paridade total entre Codex, Claude, Devin e Copilot sem evidência por capability.
- Declaração de suporte Python para versões que não tenham sido executadas e registradas.
- Fan-out ilimitado, consenso implícito ou debate sem budget e replay.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 4 perguntas de descoberta, incluindo amostras |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 5 limites de implementação; nenhuma das 7 frentes solicitadas foi removida |
| Validations Completed | 4 checkpoints; 2 mínimos exigidos |
| Duration | uma sessão |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md`
