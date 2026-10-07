# DEFINE: API Forge Observability Control Plane

> Control plane agentico para observar, analisar e governar observabilidade de APIs e do próprio API Forge.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_OBSERVABILITY_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 15/15 |

---

## Problem Statement

Engenheiros precisam observar o Runtime Agentico do API Forge e APIs externas em Java, Go e Python de forma consistente entre local, CI, AWS, Kubernetes e VMs, mas hoje os sinais estão dispersos entre OTel, CloudWatch/X-Ray e futuros vendors, sem um contrato canônico para SLOs, performance, drift, monitores, dashboards e decisões agenticas seguras. Isso dificulta detectar regressões, comparar Datadog e Dynatrace, gerar configurações reproduzíveis e aplicar mudanças com evidência, aprovação e rollback.

O problema será resolvido por um control plane provider-neutral, com OTel como caminho comum e adapters/capabilities nativos de Datadog e Dynatrace governados por policy.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Engenheiro de software | Desenvolve e evolui APIs Java, Go e Python | Não consegue correlacionar uma mudança de código com latência, erros, dependências e SLO. |
| Engenheiro de plataforma/SRE | Opera serviços em múltiplos ambientes e vendors | Precisa manter monitores, SLOs, dashboards e alertas consistentes sem configurar tudo manualmente. |
| Engenheiro de dados | Mantém APIs e integrações com bancos/eventos | Precisa observar qualidade, custo, lineage e impacto de dependências de dados. |
| Supervisor/agent | Coordena tarefas e especialistas | Precisa de fatos canônicos, capabilities, limites e evidências para decidir sem alucinar ou ampliar escopo. |
| Operador/aprovador | Autoriza ações de observabilidade | Precisa revisar diff, risco, impacto, credencial referenciada, rollback e auditoria antes de mutar vendors. |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Instrumentar e observar o próprio Runtime Agentico, correlacionando task, run, revision, agent, capability, tool, trace, span, métrica, log, evento e evidência. |
| **MUST** | Normalizar OTel/OTLP, exports sintéticos Datadog/Dynatrace e dumps CloudWatch/X-Ray em contratos canônicos versionados, com proveniência, redaction e limitações explícitas. |
| **MUST** | Analisar RED/USE, latência p50/p95/p99, erro, throughput/TPS observado, saturação, disponibilidade, cardinalidade, SLO, error budget, burn rate e drift sem inventar dados ausentes. |
| **MUST** | Gerar intents e diffs determinísticos para monitores, alertas, SLOs, dashboards, queries, deployment markers e links de exploração, preservando diferenças entre Datadog e Dynatrace. |
| **MUST** | Operar com `discover → normalize → analyze → plan → dry-run → approve → apply → verify → rollback/accept`, com mutações externas bloqueadas por padrão e auditadas quando aprovadas. |
| **MUST** | Suportar execução local/CI sem credenciais reais, usando fixtures sintéticas e adapters fake/replay determinísticos. |
| **MUST** | Integrar agents especialistas, debates, critic adversarial, referee e hold/review no Runtime Agentico existente. |
| **SHOULD** | Produzir recomendações ou artefatos de instrumentação OTel para Java, Go e Python, sem exigir uma matriz completa de SDKs. |
| **SHOULD** | Suportar discovery e capabilities declaradas para local, CI, AWS, Kubernetes externo e hosts/VMs. |
| **SHOULD** | Oferecer broker opcional de credenciais short-lived, com least privilege, TTL, referências e auditoria, sem secrets no core. |
| **COULD** | Adicionar recursos exclusivos avançados de cada vendor além de monitores, SLOs, dashboards, exploração, eventos e deployment markers. |
| **COULD** | Adicionar reconciliação contínua, incidentes autônomos, auto-remediação, UI web e modelo SaaS multi-tenant. |

**Priority Guide:**
- **MUST** = MVP fails without this (non-negotiable for MVP)
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes:

- [ ] SC-001: Um fixture OTLP/JSON do Runtime Agentico é normalizado com pelo menos 99% dos campos obrigatórios do contrato e mantém correlação task/run/agent/tool/trace/span.
- [ ] SC-002: O pipeline canônico processa deterministicamente pelo menos 10.000 spans sintéticos em CI, sem credenciais, rede ou acesso a Datadog/Dynatrace.
- [ ] SC-003: A análise produz p50, p95, p99, taxa de erro, throughput observado, saturação, disponibilidade, cardinalidade e gaps; cada valor tem origem ou é marcado como ausente/inconclusivo.
- [ ] SC-004: Pelo menos 8 cenários de eval cobrem healthy, 5xx, p99 degradado, trace quebrado, cardinalidade alta, SLO violado, drift e divergência vendor.
- [ ] SC-005: Datadog e Dynatrace expõem uma matriz de capabilities versionada para consulta e para intents de monitor, SLO, dashboard, evento e deployment marker.
- [ ] SC-006: Para a mesma entrada canônica, o control plane produz diffs reproduzíveis e não afirma equivalência quando os vendors possuem semânticas diferentes.
- [ ] SC-007: 100% das operações mutáveis passam por dry-run, policy, referência de credencial, diff, aprovação, auditoria e verificação; sem aprovação, nenhuma chamada mutável é executada.
- [ ] SC-008: Nenhum secret ou payload sensível aparece no core, logs, replay, artefatos ou fixtures; testes cobrem redaction e allowlist.
- [ ] SC-009: O Runtime Agentico consegue produzir `DONE`, `REVIEW` ou `BLOCKED` corretamente para pelo menos 12 cenários de avaliação, sem promover `DONE` com evidência insuficiente.
- [ ] SC-010: O caminho OTel gera recomendações/artefatos verificáveis para Java, Go e Python e identifica limitações quando o framework ou ambiente não puder ser confirmado.
- [ ] SC-011: O release passa em pytest, Ruff, mypy e release gate, preservando CLI/MCP parity e replay determinístico.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Runtime instrumentation | Runtime Agentico fake executa TaskSpec selado | Control plane ingere seus eventos | Um modelo canônico correlaciona run, agent, invocation, tool, debate, critic e evidência. |
| AT-002 | OTel normalization | Fixture OTLP/JSON contém resources, traces, spans e métricas | Adapter `otel-json` é executado | Contratos canônicos são produzidos com hashes, proveniência e campos ausentes nomeados. |
| AT-003 | Datadog export | Fixture sintética contém métricas, logs, monitor, SLO e dashboard | Adapter Datadog opera em modo read-only | Dados são normalizados e capabilities nativas são declaradas sem secrets. |
| AT-004 | Dynatrace export | Fixture sintética contém entidades, métricas, SLO, dashboard e problema | Adapter Dynatrace opera em modo read-only | Dados são normalizados e diferenças de entity selector/DQL/SLO são preservadas. |
| AT-005 | Multi-environment discovery | Existem manifests para local, CI, AWS, Kubernetes e VM | Discovery é executado sem conexão externa | O resultado declara ambiente, fontes, capabilities, limitações e lacunas. |
| AT-006 | RED/USE analysis | Dataset contém requests, erros, latências, recursos e dependências | Engine calcula indicadores | p50/p95/p99, erro, throughput observado, saturação e dependências são calculados com evidência. |
| AT-007 | SLO and burn rate | Fixture contém janela, objetivo, eventos bons/ruins e tempo | Engine avalia SLO | Status, error budget, burn rate e período são calculados; ausência de dados vira inconclusive. |
| AT-008 | High cardinality | Tags contêm rota dinâmica, user id e valores explosivos | Policy de cardinalidade é aplicada | O finding identifica risco, sugere redaction/normalização e não exporta payload sensível. |
| AT-009 | Monitor intent | O agente propõe monitor de p99 ou erro | Control plane gera plan | Surge um intent versionado, com query, thresholds, janela, severidade, owner, evidência e diff. |
| AT-010 | Dashboard intent | Um SLO e seus sinais têm desired state | Planner é executado | Dashboard reproduzível é gerado com widgets, queries e links; limitações vendor-specific ficam explícitas. |
| AT-011 | Drift | Estado observado difere do desired state | Drift detector compara snapshots | Finding e diff são produzidos; nenhuma mutação acontece automaticamente. |
| AT-012 | Approval gate | Existe um diff mutável sem aprovação | Agent tenta aplicar ao vendor | Operação é recusada e registrada como `BLOCKED`/`REVIEW`, sem chamada externa mutável. |
| AT-013 | Approved apply | Policy permite ambiente e operação; broker fornece referência short-lived; aprovação existe | Adapter executa apply | Apenas a capability aprovada é chamada, com auditoria, receipt e vínculo ao diff. |
| AT-014 | Verify and rollback | Apply altera estado e verificação detecta divergência | Supervisor processa resultado | Rollback plan é proposto/executado somente sob policy; estado final e evidência são registrados. |
| AT-015 | Agent debate | Specialists discordam sobre SLO, threshold ou causa | Critic e referee são acionados | Posições citam evidências; decisão resolvida ou `REVIEW`/humana é registrada. |
| AT-016 | Provider-neutral safety | Adapter retorna schema inválido ou erro de rate limit | Runtime processa resposta | Erro é estruturado, retry/backoff respeita policy e nenhuma conclusão sem prova vira `DONE`. |
| AT-017 | Instrumentation guidance | API Java, Go ou Python é descoberta | Agent de instrumentation analisa o projeto | O plano recomenda OTel e correlaciona framework, endpoints e limitações sem inventar integração. |
| AT-018 | Replay | A mesma fixture e policy são reexecutadas | Control plane gera replay | Hashes, intents, findings e status permanecem reproduzíveis, excluindo valores voláteis. |

---

## Out of Scope

Explicitly NOT included in this feature:

- Auto-remediação autônoma em produção ou mudanças sem aprovação explícita.
- SaaS multi-tenant, UI web completa e gestão organizacional de usuários.
- RUM, synthetic monitoring, continuous profiler e segurança vendor-specific avançada.
- Paridade forçada entre Datadog e Dynatrace; capabilities podem ser assimétricas.
- Reconciliação contínua 24/7 sem execução explícita ou CI.
- Dependência obrigatória de exports reais, tenants reais ou credenciais reais no CI.
- Matriz completa de SDKs e versões para Java, Go e Python.
- Substituição do TaskSpec, verifier, graphify, TokenSave ou policy engine existentes.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | OTel é o caminho canônico; Datadog/Dynatrace são adapters e capabilities. | Core não pode depender de SDK vendor-specific. |
| Security | Zero secrets no core; apenas referências a credenciais e broker opcional. | Logs, replay e artefatos devem ter redaction, allowlists e testes de exfiltração. |
| Safety | Mutação exige dry-run, diff, policy, approval, audit, verify e rollback. | Apply deve ser separado de análise e não pode ser inferido por modelo. |
| Runtime | Agents operam sob limites de calls, rounds, concorrência, timeout e rate limits. | Supervisor precisa preservar estado, cancelamento, retry bounded e REVIEW. |
| Compatibility | Deve funcionar local/CI e declarar suporte por local, CI, AWS, Kubernetes e VM. | Adapters precisam expor capabilities e limitações por ambiente. |
| Data | Cardinalidade, retenção, custo, PII e payloads sensíveis são riscos de primeira classe. | Contratos devem separar dimensões permitidas, atributos redacted e dados proibidos. |
| Testing | Sem samples reais atualmente. | Fixtures sintéticas devem representar vendor schemas e erros; exports reais entram depois. |
| Existing architecture | Reusar TaskSpec, runtime, graphify, PerformanceRun, OTel adapter, CLI/MCP e release gate. | Evitar sistemas paralelos de estado, governança e evidência. |
| Infrastructure | IaC pode gerar planos, mas apply externo é governado. | Terraform/AWS/Kubernetes integration starts as discovery/plan/diff. |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/observability/`, `src/apiforge/contracts/`, `src/apiforge/adapters/`, `src/apiforge/runtime/`, `src/apiforge/rules/`, `tests/`, `agents/`, CLI/MCP | Control plane, contratos, adapters, policies, agents e interfaces devem seguir os padrões existentes. |
| **KB Domains** | `data-quality`, `genai`, `terraform`, `aws`, `streaming`, `pydantic`, `python`, skills locais de observabilidade/performance/runtime | Design deve consultar observability, guardrails, evals, OTel, desired state, AWS e contratos. |
| **IaC Impact** | Modify existing + new adapter configuration; no mandatory live provisioning in MVP | Adapters podem gerar plans/intents; recursos reais e credenciais são opcionais e gated. |

**Why This Matters:**

- **Location** → O control plane precisa reutilizar as fronteiras de runtime, adapters, contracts e graphify.
- **KB Domains** → O design precisa cobrir observabilidade, SRE/SLO, agent safety, evals, IaC, AWS e schemas.
- **IaC Impact** → Desired state, drift e apply exigem desenho explícito de planos, credenciais e aprovação.

---

## Data Contract (if applicable)

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Runtime Agentico | Event/trace/metric/log | MVP synthetic; target 10k spans/run | Per run/CI | API Forge |
| OTLP/JSON | Trace, metric, log export | Unknown until real samples | Batch/export | Application team |
| Datadog | Vendor API/export | Unknown | Query/run based | Platform/SRE |
| Dynatrace | Vendor API/export | Unknown | Query/run based | Platform/SRE |
| CloudWatch/X-Ray | AWS dump | Unknown | Snapshot | Cloud/platform team |
| Kubernetes/AWS/VM discovery | Resource/config metadata | Unknown | Discovery execution | Platform team |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `resource_id` | string | Stable within source; provenance required | No |
| `service_name` | string | Required for service correlation | No, policy-controlled |
| `environment` | enum/string | local, ci, aws, kubernetes, vm or declared extension | No |
| `trace_id` / `span_id` | string | Valid correlation format when present | No |
| `operation` / `route_template` | string | Prefer normalized route; no raw user ids | Possible, redact |
| `timestamp` / `duration_ms` | timestamp/number | Deterministic parsing; timezone explicit | No |
| `status` / `error_class` | enum/string | Structured HTTP/RPC/vendor status | No |
| `attributes` | JSON object | Allowlist, bounded cardinality and redaction | Possible |
| `metric_value` | number | Unit and aggregation required | No |
| `slo_target` / `error_budget` | number | Range and window required | No |
| `provenance` | JSON object | Source, hash, adapter and observed_at | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Local fixtures | Deterministic per execution | Fixture hash and replay digest |
| CI exports | Available before analysis job | Input timestamp, source hash and job receipt |
| Live vendor query | Declared by adapter; no invented freshness | Query timestamp, response metadata and rate-limit state |

### Completeness Metrics

- 100% dos findings precisam indicar quais sinais foram observados e quais ficaram ausentes.
- Pelo menos 99% dos spans válidos do fixture devem sobreviver à normalização ou gerar diagnóstico explícito.
- Zero secrets e zero payloads sensíveis não permitidos no contrato, replay, logs ou fixtures.
- 100% dos intents mutáveis devem possuir owner, environment, capability, diff, approval state e rollback reference.

### Lineage Requirements

- Rastrear source → adapter → canonical telemetry → metric/SLO → finding → agent artifact → intent/diff → receipt.
- Associar traces e métricas ao serviço, endpoint, deployment, ambiente, banco/evento quando disponível e run do API Forge.
- Permitir impacto e trace reverso por graphify sem substituir a proveniência dos contratos.
- Preservar vendor query, entity selector, DQL, monitor id ou dashboard id como referência redacted e versionada.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | OTel/OTLP é suficiente como base comum para instrumentação e ingestão inicial. | Será necessário ampliar adapters e contratos antes do primeiro slice. | [ ] |
| A-002 | Datadog e Dynatrace permitem separar consultas read-only de operações mutáveis por capability/permissão. | Broker e policy precisarão de modelo mais específico por vendor. | [ ] |
| A-003 | Fixtures sintéticas podem representar schemas e erros reais até chegarem exports anonimizados. | Contract tests de vendors ficarão bloqueados ou precisarão de samples oficiais. | [ ] |
| A-004 | O Runtime Agentico pode emitir eventos suficientes para correlacionar agents, tools, tasks e evidências. | Será necessário instrumentar novos pontos do supervisor antes da análise. | [ ] |
| A-005 | SLO/RED/USE podem ser calculados sem inferir dados ausentes. | Algumas análises precisarão terminar em `REVIEW`/`INCONCLUSIVE`. | [ ] |
| A-006 | Um broker opcional pode fornecer short-lived credentials sem persistir secrets no core. | Apply vendor-specific fica restrito a dry-run até novo desenho de segurança. | [ ] |
| A-007 | AWS, Kubernetes e VMs podem ser descritos por adapters de discovery sem provisionamento obrigatório. | O multiambiente precisará ser dividido em features específicas. | [ ] |
| A-008 | Datadog e Dynatrace terão capacidades assimétricas documentáveis. | Uma camada de compatibilidade mínima será necessária para o ciclo comum. | [ ] |

**Note:** Critical assumptions must be validated during DESIGN and fixture/eval implementation.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Dor, usuários, impacto e solução-alvo estão claros. |
| Users | 3 | Cinco personas foram identificadas com dores operacionais específicas. |
| Goals | 3 | Metas MUST/SHOULD/COULD cobrem runtime, vendors, segurança e multiambiente. |
| Success | 3 | 11 critérios mensuráveis e 18 acceptance tests foram definidos. |
| Scope | 3 | MVP, vendor capabilities e out-of-scope estão explicitamente delimitados. |
| **Total** | **15/15** | Pronto para Design. |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

- Quais versões mínimas e modos de autenticação devem ser suportados pelos APIs de Datadog e Dynatrace; validar no DESIGN contra adapters e capabilities atuais.
- Qual subconjunto de schemas nativos de monitor, dashboard e SLO será obrigatório no primeiro vertical slice de cada vendor.
- Quais atributos de deployment, tenant, serviço e endpoint serão permitidos por padrão na política de cardinalidade/redaction.
- Como o broker de credenciais será conectado a AWS Secrets Manager, SSM, Kubernetes Secrets ou outro mecanismo sem entrar no core.
- Qual formato de desired state deve ser compartilhado entre OTel, Datadog, Dynatrace e Terraform sem apagar diferenças nativas.
- Como validar apply/rollback sem tenants reais: mock server, contract fixtures, sandbox vendor ou adapter fake.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-22 | define-agent | Requirements extracted from approved brainstorm; clarity 15/15. |
| 1.1 | 2026-09-22 | ship-agent | Shipped and archived after build verification. |

---

## Next Step

**Archived:** `.claude/sdd/archive/API_FORGE_OBSERVABILITY_CONTROL_PLANE/`
