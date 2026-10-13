# DEFINE: API Forge Platform Completion

> Corrigir o núcleo da API Forge e consolidar uma plataforma de engenharia de software baseada em agents, contratos, evidências e verticais governadas.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_PLATFORM_COMPLETION |
| **Date** | 2026-09-22 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |

---

## Problem Statement

A API Forge possui uma base determinística e auditável, mas gaps no extrator, nos contratos da CLI, na cadeia de evidências, na cobertura de fixtures, na documentação e na preparação dos agents impedem seu uso confiável como plataforma abrangente de engenharia de software. Engenheiros de diferentes níveis precisam receber recomendações contextualizadas, boas práticas, alternativas arquiteturais e planos verificáveis sem que o sistema invente fatos ou esconda incertezas.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Engenheiro iniciante | Desenvolvedor aprendendo práticas de engenharia | Precisa de recomendações explicadas, seguras e acompanhadas de contexto, limitações e próximos passos. |
| Engenheiro intermediário | Profissional que constrói e mantém APIs e sistemas | Precisa analisar, construir, testar e evoluir APIs, dados, mensageria e pipelines com orientação contextual. |
| Engenheiro especialista | Arquiteto, SRE, security ou platform engineer | Precisa de governança, evidências, comparação de arquiteturas, automação controlada e integração com ferramentas reais. |
| Maintainer da API Forge | Responsável pelo produto e seus adapters | Precisa de contratos, capability matrix, fixtures, agents, release evidence e compatibilidade entre CLI, MCP, IDE e UI. |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Corrigir o extrator FastAPI, `next-step` e demais fluxos críticos para que entradas suportadas ou explicitamente `unresolved` não produzam tracebacks não governados. |
| **MUST** | Fazer a cadeia `analyze -> next-step -> graph -> evidence -> brief` funcionar integralmente com os formatos oficiais de artefatos. |
| **MUST** | Criar contracts e uma capability matrix que classifiquem cada capacidade como `supported`, `heuristic`, `unresolved` ou `unsupported`, com limitações e verificador. |
| **MUST** | Preparar os agents e skills para entender a necessidade, pedir contexto quando faltar informação, recomendar boas práticas e arquiteturas, declarar premissas e preservar evidências. |
| **MUST** | Cobrir seis verticais iniciais — APIs, bancos, mensageria, CI/CD, cloud e front-end — com fixtures, casos golden, holdouts, documentação e verificação. |
| **SHOULD** | Expor os mesmos contratos e decisões por CLI, MCP, IDE e interface visual, evitando divergência entre superfícies. |
| **SHOULD** | Integrar Git, CI/CD, IDE, cloud, bancos, mensageria e ferramentas externas por adapters governados, com credenciais, policy, aprovação e rollback explícitos. |
| **COULD** | Adicionar otimizações avançadas de experiência visual, recomendações personalizadas e novos providers depois que a matriz de suporte existente estiver comprovada. |

**Priority Guide:**
- **MUST** = MVP fails without this (non-negotiable for MVP)
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] Zero tracebacks não governados nos fluxos críticos para entradas suportadas ou estados explicitamente `unresolved`.
- [ ] Uma execução completa de `analyze -> next-step -> graph -> evidence -> brief` valida os contracts oficiais e produz evidências verificáveis.
- [ ] Cada uma das seis verticais possui pelo menos uma fixture, um caso golden e um holdout executável.
- [ ] Cem por cento das capabilities públicas possuem documentação, limitações, estado de suporte e um verificador nomeado.
- [ ] Cem por cento das recomendações dos agents em casos avaliados citam os fatos disponíveis, diferenciam premissas de observações e preservam gaps não resolvidos.
- [ ] CLI, MCP, IDE e interface visual consomem os mesmos contracts para a mesma decisão, sem divergência de resultado.
- [ ] A evidência SDD e o release gate refletem o estado atual: testes, lint, tipos, checks de release e manifests devem ser reexecutáveis e consistentes.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Entrada suportada sem traceback | Um projeto coberto por um adapter suportado | Executar `discover`, `model`, `analyze` ou `index build` | O comando termina com payload contratual; qualquer limitação é `unresolved`, `refused`, `not_observed` ou `inconclusive`, nunca traceback não governado. |
| AT-002 | Roteamento de findings | `analyze` produz o formato oficial de `findings.json` | Executar `next-step` na fase válida | O agent recomendado é retornado a partir dos findings, sem erro de validação do envelope JSON. |
| AT-003 | Cadeia ponta a ponta | Um case íntegro com API-IR, facts e findings | Executar `analyze -> next-step -> graph -> evidence -> brief` | Cada etapa consome o contrato anterior, preserva hashes, nomeia gaps e produz o próximo artefato esperado. |
| AT-004 | Autoanálise do repositório | O próprio repositório API Forge contém padrões não literais e adapters diversos | Executar a análise do projeto | O resultado classifica limitações e rotas não resolvidas; nenhum `KeyError` ou traceback bruto escapa da CLI. |
| AT-005 | Capability matrix | Uma capability pública é registrada | Consultar a matriz e sua documentação | O registro contém estado de suporte, limites, evidência, pré-requisitos, risco, rollback e verificador. |
| AT-006 | Cobertura por vertical | Cada vertical possui uma fixture, um golden e um holdout | Executar a matriz de laboratório | Todas as seis verticais são descobertas e os casos são executáveis; célula sem artefato falha nomeando a lacuna. |
| AT-007 | Agent sem evidência suficiente | Um caso contém dados incompletos ou contraditórios | Solicitar recomendação ao agent | O agent pede contexto ou responde `unresolved`, separa fato de hipótese e não inventa versão, custo, throughput, permissão ou capability. |
| AT-008 | Recomendação arquitetural | Um caso declara necessidade, restrições e alternativas possíveis | Solicitar decisão a um agent especialista | A resposta apresenta recomendação, alternativas, trade-offs, risco, premissas, evidências e próximo verificador. |
| AT-009 | Mutação externa protegida | Uma ação Git, CI/CD, cloud, banco ou mensageria é classificada como mutável | Solicitar a execução sem policy/aprovação/rollback | A ação é bloqueada ou colocada em gate, com requisitos faltantes nomeados; nada é alterado. |
| AT-010 | Paridade de superfícies | CLI, MCP, IDE e UI solicitam a mesma capability | Executar a decisão em cada superfície | Todas usam o mesmo contract e retornam decisão equivalente, variando apenas apresentação. |
| AT-011 | Evidência atualizada | O código ou um contract mudou | Executar SDD, testes e release checks | O resultado identifica evidência desatualizada ou produz novos hashes; documentos antigos não são tratados como prova atual. |

---

## Out of Scope

Explicitly NOT included in this feature:

- Experiência guiada obrigatória baseada em wizard ou persona; agents adaptativos e documentação contextual são o mecanismo principal.
- Mutação externa automática sem adapter, policy, aprovação, evidência e rollback.
- Declarar suporte de produção apenas porque existe um parser, um agent ou uma integração nominal.
- Entregar todas as integrações em uma única mudança monolítica; as verticais permanecem no escopo, mas serão entregues em ondas verificadas.
- Introduzir SDK de modelo, AWS, banco ou broker diretamente no núcleo determinístico.
- Aceitar números de performance, custos, versões, permissões ou capacidades que não tenham evidência declarada.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | O núcleo permanece offline-first, determinístico e sem SDKs de modelos ou provider SDKs diretos. | Integrações externas precisam de adapters separados e resultados com proveniência. |
| Technical | `unresolved`, `refused`, `not_observed`, `inconclusive` e `confirmed` devem permanecer distintos. | Erros e ausência de prova não podem ser convertidos em sucesso implícito. |
| Technical | CLI, dispatch, MCP, skills, agents e host mirrors devem permanecer compatíveis. | Toda capability exige parity tests e contrato comum. |
| Safety | Ações cloud, database, broker, Git e CI/CD precisam de policy, aprovação, evidência e rollback quando mutáveis. | O produto pode recomendar sem executar, ou bloquear uma ação sem requisitos. |
| Repository | Alterações devem ocorrer em sandbox, branch ou worktree; o núcleo não escreve diretamente no ambiente principal. | Build e promoção precisam de diff, verificação independente e receipt. |
| Resource | A cobertura final é ampla e será sequenciada por dependências e evidência. | O roadmap deve separar foundation, verticais e integrações sem remover a visão de produto. |
| Timeline | Prazo de entrega global ainda não foi definido. | Design deve propor fases, dependências e critérios de saída antes de estimar. |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/`, `agents/`, `docs/`, `tests/`, `.claude/sdd/features/` e futuras superfícies de integração | O núcleo, contracts, adapters, agents, skills, fixtures e documentação devem permanecer separados. |
| **KB Domains** | `genai`, `prompt-engineering`, `python`, `pydantic`, `testing`, `terraform`, `cloud-platforms` e packs API Forge de contratos, segurança, performance, observabilidade e dados | Design deve consultar padrões por vertical e registrar a fonte usada em recomendações. |
| **IaC Impact** | Modify existing adapters; new integration resources TBD | Terraform/SAM e cloud providers entram por leitura governada e gates de mutação; não há autorização para mutar infraestrutura nesta fase. |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → Design phase pulls correct patterns from `${CLAUDE_PLUGIN_ROOT}/kb/`
- **IaC Impact** → Triggers infrastructure planning, avoids "works locally" failures

---

## Data Contract (if applicable)

> The feature has data and infrastructure verticals. Production source systems are not assumed; fixtures and offline artifacts are the initial evidence boundary.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| API fixtures | Código, OpenAPI, GraphQL, protobuf ou AsyncAPI | TBD | Versionada no repositório | Maintainer da vertical API |
| Database fixtures | Código, schema, migration e access reports | TBD | Versionada ou capturada com hash | Maintainer da vertical data |
| Messaging fixtures | Tópicos, filas, políticas e reports | TBD | Versionada ou capturada com hash | Maintainer da vertical messaging |
| CI/CD fixtures | Pipelines, manifests e tool reports | TBD | Atualizada junto ao pipeline | Maintainer da vertical delivery |
| Cloud fixtures | Terraform/SAM e dumps read-only | TBD | Deve declarar timestamp e origem | Maintainer da vertical cloud |
| Front-end fixtures | Código, build metadata e API integration contracts | TBD | Versionada no repositório | Maintainer da vertical frontend |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `fact_id` | String | Obrigatório, estável e ligado à proveniência | No |
| `artifact_hash` | String | SHA-256 do artefato declarado | No |
| `status` | Enum | `confirmed`, `unresolved`, `refused`, `not_observed` ou `inconclusive` | No |
| `evidence_refs` | Array[String] | Cada decisão deve apontar para evidência ou gap | No |
| `capability_state` | Enum | `supported`, `heuristic`, `unresolved` ou `unsupported` | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Local facts and contracts | Recalculados quando inputs ou hashes mudarem | Comparação de input hashes e case manifest |
| External read-only evidence | Timestamp e origem declarados em cada artifact | Receipt, source metadata e policy record |
| Release evidence | Reexecutada no estado candidato antes do ship | Testes, lint, types, SDD check e release manifest |

### Completeness Metrics

- Zero artifacts críticos sem hash ou referência de origem.
- Seis verticais com pelo menos uma fixture, um golden e um holdout.
- Cem por cento das capabilities públicas com documentação, limitações e verificador.

### Lineage Requirements

- Cada finding deve apontar para facts ou para um diagnóstico explícito.
- Cada recomendação de agent deve separar fatos observados, premissas e lacunas.
- Cada decisão deve poder ser rastreada até contract, evidence, policy e verificador.
- Mudanças de schema, capability ou adapter devem atualizar o impacto e a evidência dependente.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | A modularidade existente em core, contracts, adapters e agents pode suportar a expansão por verticais. | Será necessário separar componentes ou criar um novo boundary antes de integrar superfícies. | [x] |
| A-002 | Os adapters externos podem declarar capacidade e nível de evidência sem executar mutação por padrão. | Será necessário criar um broker de credenciais e um runtime de isolamento antes das integrações. | [ ] |
| A-003 | É possível criar projetos de exemplo representativos para APIs, bancos, mensageria, CI/CD, cloud e front-end. | A validação de agents ficará inconclusiva e o escopo de suporte terá de ser reduzido ou faseado. | [ ] |
| A-004 | CLI, MCP, IDE e UI podem consumir contracts canônicos comuns. | Será necessário criar projeções específicas e uma camada de compatibilidade entre superfícies. | [ ] |
| A-005 | O ambiente de desenvolvimento pode instalar e executar as ferramentas necessárias para as verticais. | Parte das verificações terá de permanecer import-only, fixture-only ou `unsafe_to_run`. | [ ] |
| A-006 | A entrega sequenciada por verticais é aceita enquanto todas as verticais permanecem no escopo estratégico. | Será necessário escolher entre reduzir escopo ou aceitar uma entrega monolítica de maior risco. | [x] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Gaps, impacto e necessidade de confiabilidade estão explicitamente definidos. |
| Users | 3 | Iniciante, intermediário, especialista e maintainer foram identificados com dores distintas. |
| Goals | 3 | Objetivos estão priorizados em MUST/SHOULD/COULD. |
| Success | 3 | Gate de zero tracebacks, cadeia ponta a ponta, seis verticais e coverage documental/verificável foi confirmado. |
| Scope | 3 | Escopo final, ondas de entrega e exclusões de segurança estão explicitados. |
| **Total** | **15/15** | Pronto para Design; escolhas de arquitetura e providers continuam sendo responsabilidade da próxima fase. |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

These are intentionally deferred to Design and do not block the requirements phase:

- Quais providers e ferramentas específicas devem ser a primeira implementação de cada vertical?
- Qual combinação de IDEs e protocolo de integração terá prioridade?
- Quais componentes exigem UI própria e quais devem permanecer CLI/MCP-first?
- Qual política de credenciais e quais ambientes read-only estarão disponíveis para testes externos?
- Qual envelope de tempo, custo e recursos deve ser usado por capability?
- Como será feita a aceitação humana dos ground truths e recomendações dos agents?

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Requisitos capturados a partir do BRAINSTORM aprovado; gate de sucesso confirmado; clareza 15/15. |
| 1.1 | 2026-09-22 | ship-agent | Feature implementada, documentada e arquivada. |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_PLATFORM_COMPLETION/`
