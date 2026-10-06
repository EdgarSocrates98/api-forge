# DEFINE: API Forge Agentic Experience and Interoperability

> Construir uma experiência TUI canônica e completar as bases de evidência, conhecimento, interoperabilidade, compatibilidade, CLI e debate do API Forge.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY |
| **Date** | 2026-09-23 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Built) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

Desenvolvedores e equipes de governança ainda precisam combinar CLI, arquivos, contratos e adapters para operar o kernel agêntico, porque não existe uma experiência terminal unificada nem contratos completos para Evidence Levels, Knowledge Pack freshness, negociação de hosts, matriz Python, CLI modular e debate adaptativo. Isso reduz a ergonomia, dificulta a prova de compatibilidade e aumenta o risco de claims sem evidência.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Desenvolvedor de API | Inicia, acompanha, revisa e retoma evoluções | Não possui uma tela única para acompanhar runs, dependências, artifacts, gaps e próximas ações |
| Engenheiro de plataforma | Mantém runtime, policies, evidence, packs e adapters | Precisa operar estados e provas em várias superfícies sem semântica divergente |
| Maintainer de host | Integra Codex, Claude, Devin e Copilot | Não consegue separar capability declarada, capability observada e limitação específica do host |
| Revisor de qualidade | Avalia resultado, evidência e debate | Precisa de Evidence Levels, freshness, dissent, quorum e replay reproduzíveis |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Entregar uma TUI Textual/Rich com execução como entrada e governança integrada, usando os mesmos contratos de `RuntimeExperience`, ControlPlane e verifier da CLI/JSON/MCP. |
| **MUST** | Manter fallback progressivo headless e compatibilidade dos comandos expert, sem acesso direto da TUI a stores ou integrações externas. |
| **MUST** | Implementar as seis frentes subsequentes no mesmo programa: Evidence Levels completos, Knowledge Packs com freshness read-only, host capability negotiation, matriz Python observada, CLI modular e debate adaptativo bounded. |
| **SHOULD** | Publicar projection models, snapshots, receipts e evals que permitam provar paridade entre TUI, CLI, JSON e MCP. |
| **SHOULD** | Expor estados `fresh`, `stale`, `unresolved`, `unsupported`, `blocked`, `review` e `done` sem colapsar ausência de evidência em sucesso. |
| **COULD** | Adicionar temas, atalhos configuráveis, layouts alternativos e visualizações de grafo/debate além das telas essenciais. |

**Priority Guide:**
- **MUST** = MVP fails without this (non-negotiable for MVP)
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] A primeira fatia entrega pelo menos 8 fluxos canônicos na TUI: `doctor`, `status`, `review`, `evolve`, `resume`, cancelamento, navegação de evidências e navegação de capabilities/debate.
- [ ] 100% das ações da TUI passam por application services; testes de arquitetura recusam imports ou writes diretos para `RunStore`, `TaskStore` e adapters externos.
- [ ] TUI, Rich/CLI e JSON produzem projeções equivalentes para 100% dos cenários de execução cobertos por fixtures.
- [ ] Todos os contratos relevantes de artifact, run, adapter, knowledge, host e debate carregam Evidence Level explícito ou `unknown`, sem sucesso silencioso em dados legados.
- [ ] 100% dos Knowledge Packs aceitos pelo loader possuem autoridade, versão, source hash, `observed_at`, janela de freshness e estado verificável; packs stale ou sem receipt permanecem `unresolved`.
- [ ] A negociação publica uma matriz para os 4 hosts (`claude`, `gpt-codex`, `devin`, `copilot`) com capability, prerequisites, limitações e evidence refs por host.
- [ ] A matriz Python executa e registra pelo menos 2 versões suportadas, incluindo a versão baseline atual, sem extrapolar suporte para versões não executadas.
- [ ] A CLI é dividida em módulos sem quebrar 100% dos comandos expert existentes, verificado por parity tests e snapshots de payload.
- [ ] O debate adaptativo escolhe participantes, quorum e budget por risco em cenários determinísticos, preservando dissent e replay; nenhum caso obrigatório depende de provider externo.
- [ ] Cada fatia publica testes unitários, integração, golden, holdout e mutation; a suíte completa, `ruff check .`, mypy, SDD check e release gate permanecem verdes.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Inicialização TUI | O host suporta Textual/Rich e existe um workspace local | O usuário inicia a TUI | A aplicação abre a tela de execução, carrega o estado canônico e não cria um runtime paralelo |
| AT-002 | Fallback headless | O terminal não suporta TUI ou está em CI | O usuário executa o mesmo comando | Rich/CLI/JSON projeta o mesmo status, gaps, evidências e códigos da TUI |
| AT-003 | Execução e resume | Existe um control run parcial com steps, leases e artifacts persistidos | O usuário navega e chama `resume` | A TUI mostra o estado real, retoma somente trabalho elegível e preserva idempotência/replay |
| AT-004 | Governança na TUI | Existe um run com evidence, gaps, capabilities e review | O usuário abre governança e solicita review/cancelamento | A ação passa por policy/ControlPlane, registra ator/evento e atualiza a projection sem write direto |
| AT-005 | Evidence Levels | Um artifact é observed, inferred, heuristic, verified ou desconhecido | Um contrato é carregado/projetado | O nível é preservado, validado e impede `DONE` quando a prova obrigatória não existe |
| AT-006 | Knowledge Pack fresco | Um pack possui source authority, versão, hash e receipt dentro da janela | O loader e o refresh read-only são executados | O pack fica `fresh` somente com correspondência de hash e freshness verificável |
| AT-007 | Knowledge Pack stale | O receipt está expirado, ausente ou divergente | O runtime tenta usar o pack | O resultado é `stale`/`unresolved`, com código, gap e próxima ação; não há atualização mutável automática |
| AT-008 | Host capability negotiation | Quatro hosts declaram capacidades e limitações distintas | O resolver calcula a matriz | Cada host recebe somente capabilities elegíveis; ausência de prova não vira equivalência |
| AT-009 | Python compatibility matrix | Duas versões são executadas em ambientes declarados | O gate de matriz é executado | Cada célula registra resultado, ambiente, hashes e limitações; versões não executadas ficam `unresolved` |
| AT-010 | CLI modular parity | Todos os comandos expert existentes estão disponíveis | O usuário usa módulo novo e caminho legado | Ambos retornam contratos equivalentes e aliases preservados |
| AT-011 | Debate adaptativo | Um caso possui risco, budget, possíveis dissent e adapters fake | O debate é executado | A policy escolhe quorum/participantes bounded, registra posições/evidence refs e permite replay determinístico |
| AT-012 | Debate sem prova | O caso não possui evidence suficiente ou excede budget | O debate tenta fechar recomendação | O resultado permanece `REVIEW`/`BLOCKED`, preserva dissent e não inventa consenso |
| AT-013 | Slice quality gate | Uma fatia possui testes, golden, holdout e mutation declarados | O gate é executado | A fatia só passa quando casos obrigatórios e verificação independente passam |
| AT-014 | Compatibilidade | Runs, artifacts, packs e contratos v1 existentes são carregados | O novo runtime projeta os dados | Dados legados continuam legíveis; migração é aditiva, explícita e verificável |

---

## Out of Scope

Explicitly NOT included in this feature:

- Web UI pesada na primeira fase; a entrega é terminal-first.
- Mutação automática em GitHub, AWS, bancos, brokers, hosts ou providers de modelos.
- Claim de produção, freshness ou equivalência entre hosts baseado apenas em fixtures locais.
- Fan-out ilimitado, consenso implícito ou debate sem budget, quorum e replay.
- Declaração de suporte Python para versões que não tenham execução observada.
- Remoção ou quebra dos comandos expert existentes durante a modularização da CLI.

As sete frentes do pedido permanecem dentro do programa; esses itens descrevem limites de segurança e de primeira implementação, não exclusão das frentes.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Core offline-first; sem provider/model SDK direto em `src/` | Textual/Rich, receipts e adapters devem funcionar com fixtures/fakes locais |
| Technical | TUI é projection, não autoridade | Toda ação usa application service, policy, ControlPlane e verifier |
| Technical | Freshness e host negotiation são evidence-driven | Estados ausentes permanecem `unresolved`, sem inferência silenciosa |
| Compatibility | Evolução aditiva e fallback progressivo | CLI/JSON/MCP e artifacts antigos continuam legíveis |
| Quality | Cada fatia exige golden, holdout, mutation e verificação independente | Uma feature visual não passa sem prova comportamental |
| Resource | Docker é opcional e não amplia claims | Validações principais devem funcionar no checkout e na virtualenv local |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/tui`, `src/apiforge/application`, `src/apiforge/contracts`, `src/apiforge/knowledge`, `src/apiforge/agentops`, `src/apiforge/debate`, `tests/` | TUI e contratos vivem no core local; adapters externos permanecem read-only |
| **KB Domains** | `genai`, `python`, `testing`, `prompt-engineering`, `data-quality` | State machines, guardrails, schemas, snapshots, evals e freshness |
| **IaC Impact** | None for first program slice | Nenhum recurso de infraestrutura novo é necessário; Docker só apoia prova local opcional |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `${CLAUDE_PLUGIN_ROOT}/kb/`
- **IaC Impact** → No infrastructure planning is required for the offline-first slice

---

## Data Contract (if applicable)

Knowledge Packs, host declarations, Python matrix results e debate receipts são artefatos locais versionados ou observações read-only.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| `knowledge/` | Local versioned packs | Unknown; measured by loader | Source metadata + declared window | Project maintainers |
| External read adapters | HTTP GET/receipt | Bounded per policy | Declared by receipt and verified at read time | Adapter policy |
| Host declarations | Local manifests/configuration | 4 named hosts initially | At declaration/receipt time | Host adapter |
| Python matrix runs | CI/local execution artifacts | At least 2 versions in first matrix | Per run | Verification gate |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `source_authority` | string | Required for accepted pack | No |
| `source_version` | string | Required and stable | No |
| `source_hash` | string | SHA-256 or explicit unresolved | No |
| `observed_at` | ISO timestamp | Explicit clock source | No |
| `freshness_window` | duration/string | Declared; no implicit default | No |
| `evidence_level` | enum | Required or `unknown` | No |
| `status` | enum | `fresh`, `stale`, `unresolved`, `verified` | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Local pack | Fresh only inside its declared window | Hash, version and timestamp comparison |
| External receipt | No universal SLA; each source declares its window | Receipt verification without contacting provider |
| Host/Python matrix | Valid only for the declared run/environment | Execution receipt and input hashes |

### Completeness Metrics

- 100% dos packs aceitos carregam source authority, version, hash e freshness state.
- 100% das host declarations carregam capability, prerequisites e limitações.
- 100% das células Python publicadas carregam ambiente, resultado e hashes.
- 100% dos debates fechados carregam posições, evidence refs, budget e replay id.

### Lineage Requirements

- Cada projection deve apontar para run/control id e artifact/evidence hashes.
- Cada pack refresh deve apontar para source authority, receipt e versão.
- Cada host capability deve apontar para declaration/evidence refs.
- Cada debate deve apontar para seus inputs, adapters, policy, dissent e resultado.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Textual/Rich pode ser tratado como dependência opcional ou controlada no ambiente local | Será necessário um fallback Rich/CLI mais amplo ou outro toolkit terminal | [ ] |
| A-002 | `RuntimeExperience` consegue projetar todos os estados sem expor stores diretamente | Será necessário ampliar a facade antes da TUI | [ ] |
| A-003 | Os quatro hosts podem fornecer declarations locais comparáveis por schema comum | Negotiation começará como matriz por host com gaps explícitos | [ ] |
| A-004 | Pelo menos duas versões Python podem ser executadas nos ambientes disponíveis | A matriz ficará parcialmente `unresolved` até CI/worktrees adicionais | [ ] |
| A-005 | Knowledge Packs atuais podem receber metadados aditivos sem quebrar o loader fechado | Será necessário versionar schema e adaptar packs antes do refresh | [ ] |
| A-006 | Adapters fake são suficientes para validar o debate antes de provider externo | A integração real será separada por receipt e policy gate | [ ] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Dor, impacto e ausência de superfície unificada estão explícitos |
| Users | 3 | Desenvolvedor, plataforma, host maintainer e revisor identificados |
| Goals | 3 | TUI prioritária e seis frentes subsequentes com prioridades claras |
| Success | 3 | Critérios numerados para fluxos, hosts, versões, parity e gates |
| Scope | 3 | Todas as sete frentes permanecem em escopo; limites de segurança estão explícitos |
| **Total** | **15/15** | Pronto para Design |

**Scoring Guide:**

- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

Nenhuma questão bloqueadora para Design. A fase de Design deverá validar, com evidência do ambiente:

- versão e estratégia de dependência Textual/Rich;
- estratégia de testes de terminal/snapshots;
- versões Python que podem ser executadas no CI/local;
- esquema de migration dos Knowledge Packs atuais;
- adapters e policy de provider para debate multi-modelo;
- decomposição da CLI sem quebrar aliases e imports públicos.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-23 | define-agent | Requirements derived from validated brainstorm; clarity 15/15 |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_API_FORGE_AGENTIC_EXPERIENCE_INTEROPERABILITY.md`
