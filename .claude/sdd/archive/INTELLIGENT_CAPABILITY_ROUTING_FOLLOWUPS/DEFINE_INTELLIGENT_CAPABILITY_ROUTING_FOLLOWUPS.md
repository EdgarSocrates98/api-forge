# DEFINE: Intelligent Capability Routing Follow-ups

> Programa de evolução do Intelligent Capability Routing com contexto versionado, planejamento adaptativo, otimização controlada, superfícies operacionais e governança externa verificável.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS |
| **Date** | 2026-09-24 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |

---

## Problem Statement

Maintainers, operadores e equipes de plataforma têm contratos básicos de Intelligent Capability Routing, mas ainda não conseguem evoluir contexto, evidência, planejamento, otimização, adapters, CLI/TUI e governança externa como capacidades independentes, auditáveis e reversíveis. O programa deve preencher essas lacunas em ondas ordenadas por dependência, sem promover comportamento adaptativo ou autoridade externa na ausência de evidência verificável.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Maintainer e operador | Mantém o runtime e investiga decisões | Precisa reconstruir por que uma rota foi escolhida, distinguir sinal de evidência e voltar a um fallback seguro. |
| Plataforma, DevEx e CI | Mantém contratos, ambientes e workflows | Precisa consumir uma superfície estável para CLI/TUI, matriz Python, adapters e gates sem duplicar regras do domínio. |
| Revisor de segurança e qualidade | Avalia risco, regressão e autorização | Precisa provar que uma mudança não ampliou autoridade, não ocultou falhas e pode ser revertida. |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Definir ondas, estados de promoção, dependências, entry/exit gates, fallback e evidências obrigatórias para os nove itens diferidos. |
| **MUST** | Garantir modos explícitos `local`, `replay`, `shadow` e `external-read`, com execução determinística quando não houver evidência ou policy suficiente. |
| **MUST** | Formalizar contratos para Evidence Coverage, Knowledge Pack/freshness, estimativa de complexidade, decisão de DAG adaptativo, capability de provider/modelo e governança externa. |
| **MUST** | Preservar a fronteira read-only: core e agentes não executam SDKs de providers, não mutam GitHub, não alteram branch protection e não fazem merge. |
| **SHOULD** | Entregar primeiro Knowledge Packs versionados, freshness explícita, adapters reais observacionais e comparação entre plano estático e adaptativo. |
| **SHOULD** | Permitir ajuste de pesos offline e bandit somente em `shadow`/simulação, com avaliação independente e rollback antes de qualquer promoção. |
| **COULD** | Evoluir CLI, TUI, matriz Python e integração de governança em fatias que consumam os contratos compartilhados. |

**Priority Guide:**

- **MUST** = o programa não é seguro ou auditável sem isso.
- **SHOULD** = importante para as primeiras fatias, mas pode ser faseado.
- **COULD** = valor posterior, cortável sem invalidar a fundação.

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] **Todas** as decisões promovidas para `active` possuem trace, versão da policy, referências de evidência, estado de freshness, resultado de avaliação e fallback registrado.
- [ ] **Nenhuma** operação externa de provider, modelo ou GitHub ultrapassa o modo autorizado; tentativas sem allowlist, credencial ou policy resultam em recusa catalogada com `AF-*`, `field` e `unlock`.
- [ ] **Todas** as comparações entre plano estático e adaptativo usam o mesmo conjunto de fixtures e registram divergência, custo observado, resultado de qualidade e decisão de promoção.
- [ ] **Todos** os pesos aprendidos permanecem offline ou em shadow até que exista baseline congelado, holdout, mutation check, gate de segurança e rollback verificável.
- [ ] **Todos** os ambientes declarados na matriz Python têm execução verificável; ambientes não testados aparecem como não suportados ou não observados.
- [ ] **Todas** as integrações de governança preservam o core read-only e delegam mutações, quando autorizadas, ao workflow dedicado com receipt independente.

Os limiares numéricos de qualidade, freshness, budget e custo serão definidos na Design por policy versionada; este DEFINE não inventa valores de runtime nem claims de produção.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Promotion evidence gate | Uma decisão está em `replay`, `shadow` ou `external-read` sem um dos artefatos obrigatórios | O supervisor tenta promovê-la para `active` | A promoção é bloqueada, o motivo é persistido e o sistema mantém fallback determinístico. |
| AT-002 | Missing or stale context | Um Knowledge Pack está ausente, inválido ou além da freshness policy | O routing solicita contexto para escolher uma rota | A decisão registra a limitação, não trata freshness como verdade e escolhe rota segura ou recusa catalogada. |
| AT-003 | Bounded adaptive DAG | O estimador propõe tarefas fora da allowlist, além do budget ou sem dependência selada | O planner tenta materializar o DAG adaptativo | A proposta é rejeitada ou reduzida ao plano estático; nenhuma autoridade adicional é concedida. |
| AT-004 | Provider capability boundary | Um adapter de provider/modelo não consegue provar versão, capability, limites ou estado | O runtime solicita capability discovery ou execução | É emitido um receipt incompleto e a execução não é promovida a claim de produção. |
| AT-005 | Learned-weight safety | Um conjunto de pesos foi produzido offline ou por bandit em shadow | Um operador tenta ativá-lo sem avaliação independente, rollback e gates completos | A ativação é bloqueada e o baseline permanece em vigor. |
| AT-006 | Evidence Coverage explainability | Uma rota adaptativa possui justificativas e evidências parciais | A métrica de Evidence Coverage é calculada | O resultado distingue cobertura, ausência e limitação; não converte evidência parcial em aprovação automática. |
| AT-007 | Shared operational contracts | CLI, TUI ou matriz Python recebe uma capacidade desconhecida ou ambiente não testado | A superfície tenta exibir ou executar a capacidade | O resultado usa o contrato compartilhado e declara `unsupported`, `unobserved` ou fallback, sem duplicar regra de domínio. |
| AT-008 | External GitHub governance boundary | Um agente, core ou adapter tenta alterar branch protection, abrir PR ou fazer merge diretamente | A operação é submetida ao runtime | A operação é recusada com `AF-*`, `field` e `unlock`; apenas o workflow autorizado pode produzir a mutação e seu receipt. |

---

## Out of Scope

Explicitly NOT included in this feature:

- Implementar os nove itens como uma única fatia ou declarar todas as ondas como entregues por este DEFINE.
- Bandit online, aprendizado autônomo de pesos ou promoção de modelo sem baseline, holdout, mutation check, safety gate e rollback.
- Importar SDKs de providers/modelos no core ou fazer claims de produção sem capability receipt e evidência externa independente.
- Fazer Knowledge Pack fresco significar automaticamente correto, completo ou confiável.
- Permitir que estimador ou DAG adaptativo remova gates, amplie allowlist, ultrapasse budget ou substitua o fallback estático sem policy.
- Reescrever toda a CLI como pré-requisito; a modularização será incremental e orientada por bounded contexts.
- Fazer TUI 2.0 antes de contratos de domínio e estados operacionais estabilizados.
- Declarar suporte na matriz Python sem execução verificável no ambiente correspondente.
- Fazer o core, agentes ou adapters mutarem branch protection, abrirem PR, fizerem merge ou alterarem governança GitHub.
- Prometer freshness externa, qualidade de provider, custo, latência ou segurança de produção sem receipt independente.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Local-first, offline-first e execução determinística na ausência de adapter/policy explícito | Contratos e runtime devem operar com fixtures, replay e fallback; integrações externas são opcionais. |
| Technical | O core não importa SDKs de providers, AWS ou bancos vivos para esta evolução | Adapters ficam em boundaries dedicados; claims são limitados ao que o receipt comprova. |
| Security | Segurança, evidência e reversibilidade têm prioridade sobre autonomia e velocidade | Nenhuma promoção sem gates; recusas preservam `AF-*`, `field` e `unlock`. |
| Governance | GitHub, branch protection, reviewers e merge são controlados por workflow e policy externa | O aplicativo e os agentes continuam read-only; receipts não provam autoria ou deployment safety. |
| Quality | Golden, holdout, mutation checks, scorecards e traces devem permanecer disponíveis | Otimização e DAG adaptativo precisam ser comparáveis ao baseline e não podem ocultar falhas. |
| Compatibility | CLI, TUI e matriz Python devem consumir contratos compartilhados | Mudanças de superfície não podem criar uma segunda implementação da regra de routing. |
| Infrastructure | Nenhum recurso de infraestrutura é criado ou alterado nesta fase | O Design deve tratar workflows e adapters como configuração/boundary, não como provisionamento do core. |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts`, `src/apiforge/knowledge`, `src/apiforge/evals`, `src/apiforge/integrations`, `src/apiforge/application`, `src/apiforge/runtime`, `src/apiforge/cli.py`, `src/apiforge/cli_tui.py`, `tests/`, `.claude/sdd/features/` | Separar contratos, orquestração, adapters, superfícies e documentação SDD. |
| **KB Domains** | `genai`, `data-quality`, `python`, `pydantic`, `testing`, `airflow`, `component-model` e segurança/governança do projeto | Consultar avaliação, agentic workflow, guardrails, observabilidade/freshness, arquitetura em camadas, testes de integração e DAGs. |
| **IaC Impact** | None | Branch protection e workflows externos são boundaries de governança; não há recurso IaC a provisionar nesta fase. |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `${CLAUDE_PLUGIN_ROOT}/kb/`
- **IaC Impact** → Triggers infrastructure planning, avoids "works locally" failures

---

## Data Contract (if applicable)

> O programa trata traces, scorecards, freshness, receipts e planos como dados de decisão; qualquer fonte externa permanece read-only e com proveniência explícita.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Fixtures, golden, holdout e mutation locais | Arquivos de teste e casos versionados | Não quantificado | Reproduzível por checkout/caso | Maintainers |
| Routing traces e scorecards | Artefatos de runtime/eval | Não quantificado | Associada ao run e à policy | Runtime/evals |
| Knowledge Packs | Artefatos versionados | A definir | Policy por pack/versão | Plataforma |
| Provider/model capability receipts | Adapter externo read-only | Não observado atualmente | Freshness do receipt e janela da policy | Integrações |
| GitHub/CI governance receipts | Workflow/adaptador externo | Não observado atualmente | Freshness do estado remoto | Plataforma/CI |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `knowledge_pack_ref` | Referência versionada | Deve identificar pack e versão; ausência não pode ser ocultada | Não |
| `freshness_state` | Estado de freshness | Deve distinguir fresco, stale, desconhecido e não observado | Não |
| `evidence_refs` | Lista de referências | Deve apontar para artifacts/receipts verificáveis | Não |
| `complexity_estimate` | Estimativa determinística | Não pode conceder autoridade ou ultrapassar budget | Não |
| `adaptive_dag_decision` | Plano/decisão tipada | Deve preservar dependências, allowlist e fallback | Não |
| `provider_capability_receipt` | Receipt externo | Não pode extrapolar capability ou produção | Não; não conter segredo |
| `governance_receipt` | Receipt de workflow/policy | Não prova autoria, merge ou deployment safety por si só | Não; não conter segredo |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Local Knowledge Packs | Definido por policy versionada antes da ativação | Timestamp, hash, versão e estado de validade do pack |
| Provider/model receipts | Definido por adapter e policy; desconhecido não é sucesso | Timestamp do receipt, janela de freshness e response hash |
| GitHub/CI governance | Definido pelo workflow/policy externa | Receipt do estado remoto e indicação de limitação |

### Completeness Metrics

- Todas as decisões promovidas precisam referenciar evidência, policy, freshness, avaliação e fallback.
- Toda recusa externa precisa carregar código `AF-*`, campo rejeitado e unlock seguro.
- Todo ambiente anunciado como suportado precisa ter prova de execução; o restante permanece não observado.
- Todo plano adaptativo precisa preservar tarefas permitidas, dependências, budget, timeout e fallback.

### Lineage Requirements

- Manter lineage de request → routing → Knowledge Pack/freshness → plano → adapter → eval → promoção/fallback.
- Associar cada peso, scorecard e decisão adaptativa à versão de inputs e da policy.
- Permitir impacto reverso de uma evidência stale, receipt inválido ou mudança de contrato até as decisões afetadas.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Os contratos e feedback da primeira fatia são base estável para evolução. | Será necessário criar uma nova camada de compatibilidade antes das ondas seguintes. | [x] Parcialmente: implementação e testes da feature anterior estão commitados. |
| A-002 | Fixtures locais, traces e scorecards podem servir de baseline inicial. | A Onda 0 precisará primeiro criar datasets e instrumentos de replay. | [x] Parcialmente: existência observada; suficiência ainda não comprovada. |
| A-003 | Knowledge Packs podem ser versionados e carregados sem dependência online no core. | A arquitetura precisará separar armazenamento e resolver freshness externo. | [ ] |
| A-004 | Providers/modelos podem ser isolados atrás de adapters e receipts. | A Onda 1 ficará limitada a capability simulada/local. | [ ] |
| A-005 | Um workflow dedicado pode ser configurado com credencial mínima para mutações GitHub autorizadas. | Governança ficará read-only e sem mutação automatizada até haver policy externa. | [ ] |
| A-006 | CLI, TUI e matriz Python podem migrar incrementalmente sem quebrar contratos existentes. | Será necessária uma camada de compatibilidade ou uma fatia separada de refatoração. | [ ] |
| A-007 | Os limiares de qualidade, freshness, budget e custo serão definidos como policy, não como memória do modelo. | O Design não terá gate operacional determinístico e não poderá promover a capacidade. | [ ] |

**Risk treatment:** assumptions não validadas são riscos de Design; nenhuma deve ser convertida em claim de provider, produção ou governança.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Problema, impacto e fronteiras estão descritos para runtime e plataforma. |
| Users | 3 | Maintainer/operador, plataforma/DevEx/CI e revisão de segurança/qualidade têm dores explícitas. |
| Goals | 3 | Goals estão priorizados em MUST/SHOULD/COULD e refletem as ondas escolhidas. |
| Success | 2 | Critérios são verificáveis por artefatos e gates, mas os limiares numéricos de policy ficam para Design. |
| Scope | 3 | Os nove itens, as ondas, os limites externos e o YAGNI estão explícitos. |
| **Total** | **14/15** | Acima do gate mínimo; detalhes de limiares e contratos podem ser resolvidos em Design. |

**Scoring Guide:**

- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

Estas perguntas não bloqueiam a passagem para Design, mas precisam de resposta antes da implementação:

- Qual é a fórmula e o nível de granularidade da Evidence Coverage: por decisão, claim, tarefa, trace ou combinação?
- Quais providers/modelos entram primeiro na Onda 1 e quais capabilities podem ser observadas sem execução de produção?
- Quais freshness windows e budgets serão policy por Knowledge Pack, adapter, DAG e workflow?
- A primeira versão do DAG adaptativo apenas produz um plano comparável ou também executa tarefas dentro da mesma fatia?
- Quais versões Python e plataformas serão efetivamente executadas na matriz ampliada?
- Quais configurações e receipts pertencem ao workflow de governança GitHub sem transferir autoridade ao core?

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-24 | define-agent | Requisitos capturados a partir do brainstorm aprovado; clareza 14/15; pronto para Design. |
| 1.1 | 2026-09-24 | design-agent | Design concluído; Wave 0 delimitada para build e ondas futuras seladas por gates. |
| 1.2 | 2026-09-24 | build-agent | Wave 0 construída, validada e pronta para ship; ondas futuras permanecem seladas. |
| 1.3 | 2026-09-24 | ship-agent | Shipped and archived. |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_INTELLIGENT_CAPABILITY_ROUTING_FOLLOWUPS.md`
