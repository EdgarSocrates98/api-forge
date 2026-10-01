# BRAINSTORM: API Forge Observability Control Plane

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_OBSERVABILITY_CONTROL_PLANE |
| **Date** | 2026-09-22 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** Preparar tudo relacionado a observabilidade, Datadog e Dynatrace no API Forge, evoluindo o Runtime Agentico para observar o próprio API Forge e também APIs externas em Java, Go e Python, com SLOs, performance, dashboards, monitores, alertas, deployment markers, debates, critic, aprovação e operação segura.

**Context Gathered:**
- O Runtime Agentico 2.0 já possui supervisor determinístico, TaskSpec, policy, fan-out bounded, critic, debate, replay, artefatos e gates.
- O projeto já possui a skill `api-forge-observability`, o agente `api-observability-engineer`, `PerformanceRun`, `model otel`, adapters OTLP/JSON, fixtures OTel e playbooks CloudWatch/X-Ray.
- A implementação atual é offline/local-CI e não possui exporters Datadog/Dynatrace nem mutações externas.
- O repositório não possui `CLAUDE.md` na raiz; os contratos, skills, adapters, fixtures, evals e histórico foram usados como contexto do brainstorm.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/observability/`, `src/apiforge/contracts/`, `src/apiforge/adapters/`, `src/apiforge/runtime/` | Criar control plane e adapters sem acoplar o core ao vendor. |
| Relevant KB Domains | `data-quality/observability`, `genai/evaluation-framework`, `genai/guardrails`, `terraform`, `aws`, padrões locais de OTel e performance | Definir SLOs, evidência, segurança, IaC e evals como contratos. |
| Existing Patterns | `src/apiforge/adapters/otel/`, `PerformanceRun`, graphify, TaskSpec, policy e MCP/CLI parity | Reusar ingestão, proveniência, replay e gates existentes. |
| Vendor Evidence | OTel semantic conventions; Dynatrace OTel/API/SLO/DQL; Datadog monitor-based SLOs e APIs | Modelar capabilities e limitações por vendor, sem presumir paridade. |
| IaC Patterns | Terraform é analisado offline; não há reconciliação de observabilidade em produção | Primeiro gerar desired state, diff e plan; apply depende de aprovação. |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual o objetivo principal? | **(c) Ambos**, observando o próprio API Forge e APIs externas Java, Go e Python. | O API Forge será referência e também gerador de instrumentação/adapters. |
| 2 | Como operar Datadog/Dynatrace? | **(c) Modo híbrido**, OTel como padrão e integrações nativas quando agregarem valor exclusivo. | Evita lock-in e preserva SLOs, monitores, dashboards e eventos vendor-specific. |
| 3 | Qual autonomia? | **(c) Autonomia operacional controlada**, com policy, dry-run, diff, rollback, auditoria e aprovação. | Nenhuma mutação externa é inferida a partir de texto de modelo. |
| 4 | Quais resultados definem sucesso? | **(d) Todos**: runtime, SLO/performance e operação automatizada. | O release será dividido em slices, mas cobrirá a cadeia completa. |
| 5 | Quais amostras? | **(c)** Fixtures existentes mais exports reais anonimizados quando disponíveis; no momento não há dados reais. | Fixtures sintéticas realistas serão a fonte inicial de verdade e evals. |
| 6 | Qual abordagem? | **(c) Control plane de observabilidade**. | Centraliza normalização, análise, desired state, drift, agents e gates. |
| 7 | Quais vendor capabilities? | **(d) Ciclo completo**: monitores, SLO/confiabilidade, dashboards e exploração. | MVP maior, dividido em slices com gates independentes. |
| 8 | Quais ambientes? | **(d) Multiambiente**: local, CI, AWS, Kubernetes externo e hosts/VMs. | Adapters e capabilities deverão declarar suporte por ambiente. |
| 9 | Como tratar credenciais? | **(c)** Zero secrets no core e broker opcional para ações aprovadas. | Usar referências, short-lived credentials, least privilege, TTL e auditoria. |

**Minimum Questions:** 9

---

## Sample Data Inventory

> Não existem exports reais de Datadog/Dynatrace neste momento.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `tests/fixtures/otel/baseline.json`, `candidate.json` | 2 | OTLP/JSON sintético com traces e spans comparáveis. |
| Output examples | `src/apiforge/adapters/otel/`, `PerformanceRun` e testes de performance | Vários | Shape canônico de facts, métricas e veredictos. |
| Ground truth | Testes de `model otel`, `perf verdict`, runtime e release gate | 10+ | Resultados determinísticos e limites já verificados. |
| Related code | `src/apiforge/runtime/`, `.claude/skills/api-forge-observability/`, agentes e playbooks | Vários | Políticas, contratos, replay, proveniência e governança. |
| Future samples | Exports anonimizados Datadog/Dynatrace | 0 hoje | Entrarão como fixtures versionadas após disponibilidade. |

**How samples will be used:**

- Fixtures sintéticas serão usadas para testar normalização, correlação, cardinalidade, SLOs, divergência e vendor capability matrix.
- Exports reais futuros serão usados como contract fixtures, nunca como dependência obrigatória do CI.
- Casos sintéticos de p99 degradado, 5xx, trace quebrado, SLO violado, drift e monitor divergente alimentarão evals de routing, critic e refusal.
- Nenhum payload sensível será capturado por padrão; redaction e allowlists serão verificadas pelos testes.

---

## Approaches Explored

### Approach A: OTel Gateway + Adapters ⭐

**Description:** OTel/OTLP como caminho canônico, com Datadog e Dynatrace como exporters/query adapters e capabilities nativas opcionais.

**Pros:**
- Baixo lock-in e boa portabilidade entre Java, Go, Python, AWS, Kubernetes e VMs.
- Reaproveita o adapter OTel, `PerformanceRun`, contratos e fixtures existentes.
- Menor superfície de credenciais e melhor primeiro slice local/CI.

**Cons:**
- Recursos avançados exigem APIs específicas e não terão paridade perfeita.
- Menor capacidade de reconciliação e operação centralizada no início.

**Why not selected:** A escolha do usuário foi investir desde o início em um control plane com ciclo completo de operação.

### Approach B: Integração nativa completa por vendor

**Description:** Modelar clients e recursos específicos para métricas, traces, logs, monitores, dashboards, SLOs, eventos e deployment markers de cada plataforma.

**Pros:**
- Profundidade máxima em cada vendor.
- Acesso direto a recursos proprietários.

**Cons:**
- Alto acoplamento e duplicação de regras.
- APIs, permissões, limites e semânticas divergentes aumentam risco e custo.
- Dificulta comparação e portabilidade entre ambientes.

**Why not selected:** Deve existir como adapter/capability dentro de um control plane, não como arquitetura dominante.

### Approach C: Control Plane de Observabilidade + OTel/Vendors ⭐ Selecionada

**Description:** Control plane que descobre, normaliza, analisa, calcula SLOs, gera intents, compara desired/observed state, produz diffs e coordena adapters OTel, Datadog e Dynatrace sob policy.

**Pros:**
- Suporta o ciclo completo: discovery, SLO, monitores, dashboards, exploração, diff, aprovação, apply e verify.
- Permite agents especializados, debates e critic com evidências comuns.
- Preserva OTel como interoperabilidade e reserva APIs nativas para valor exclusivo.

**Cons:**
- Maior investimento inicial e necessidade de state/drift bem definidos.
- Requer controle rigoroso de cardinalidade, credenciais, rate limits e compatibilidade.

**Why Recommended:** É a única abordagem que atende simultaneamente runtime próprio, APIs externas, multiambiente e autonomia operacional controlada. A recomendação combina forte precedente local (OTel, TaskSpec, graphify, policy, replay) com padrões de observabilidade e agentes já presentes no projeto. Confiança: **0,95**.

---

## Data Engineering Context (if applicable)

Não é uma feature primariamente de engenharia de dados, mas usa conceitos de qualidade, lineage e drift.

### Source Systems

| Source | Type | Volume Estimate | Current Freshness |
|--------|------|-----------------|-------------------|
| OTLP/JSON | Trace/metric/log export | Desconhecido até amostras reais | Batch/export |
| Datadog | Vendor observability API/export | Desconhecido | Consulta sob demanda |
| Dynatrace | Vendor observability API/export | Desconhecido | Consulta sob demanda |
| CloudWatch/X-Ray | AWS dumps | Desconhecido | Dump offline |

### Data Flow Sketch

```text
[OTel/Datadog/Dynatrace/AWS/K8s/VM]
              ↓
        [Source Adapters]
              ↓
    [Canonical Telemetry Contract]
              ↓
 [SLO/RED/USE/Drift/Cardinality Engine]
              ↓
 [Specialists → Debate → Critic → Referee]
              ↓
 [Intent/Diff → Dry-run → Approval]
              ↓
 [Vendor Adapter Apply → Verify → Rollback/Accept]
```

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach C — Control Plane de Observabilidade + OTel/Vendors |
| **User Confirmation** | 2026-09-22 |
| **Reasoning** | Atende o ciclo completo, suporta multiambiente, mantém OTel como contrato comum e permite capacidades nativas governadas de Datadog/Dynatrace. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|---------------------|
| 1 | Observar primeiro o próprio API Forge e depois APIs externas | O runtime fornece ground truth de agents, tasks, tools, gates e replay | Construir SDKs externos antes de validar o contrato interno |
| 2 | Control plane como arquitetura | Centraliza desired state, drift, análise, evidence e governança | Adapters isolados sem visão sistêmica |
| 3 | OTel como contrato/canal padrão | Interoperabilidade e precedente local | Lock-in nativo desde a origem |
| 4 | Datadog/Dynatrace com capabilities nativas | Monitores, SLOs, dashboards e eventos agregam valor exclusivo | Forçar falsa paridade por abstração excessiva |
| 5 | Ciclo completo no MVP | Necessidade explícita do usuário | Limitar MVP apenas a ingestão |
| 6 | Multiambiente desde o início | APIs podem rodar local, CI, AWS, Kubernetes e VMs | AWS-only |
| 7 | Zero secrets no core + broker opcional | Reduz exfiltração e mantém least privilege | Credenciais persistidas no control plane |
| 8 | Mutação por policy, diff, aprovação e rollback | Autonomia segura e auditável | Apply automático por decisão de modelo |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Auto-remediação autônoma em produção | Risco alto antes de validar desired state, rollback e evidência | Yes |
| Incidente autônomo com comunicação externa | Exige integrações organizacionais e políticas de escalonamento | Yes |
| Paridade total entre Datadog e Dynatrace | Semânticas, APIs e capacidades diferem; capabilities devem explicitar limites | Yes |
| Agents próprios para todas as versões de Java/Go/Python | Primeiro slice deve provar contrato e adapters, não uma matriz infinita de SDKs | Yes |
| RUM, synthetics, profiler contínuo e segurança vendor-specific | Não são necessários para validar o control plane inicial | Yes |
| SaaS multi-tenant e UI web completa | A primeira entrega é local/CI/control-plane API e CLI/MCP | Yes |
| Reconciliação contínua 24/7 | Começar com execução explícita/CI torna auditoria e custo controláveis | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Architecture concept | ✅ | Usuário confirmou as cinco camadas do control plane. | No |
| Component breakdown | ✅ | Usuário confirmou contratos, adapters, agents, debates, gates e fixtures. | No |
| Vendor scope | ✅ | Usuário ampliou o MVP para ciclo completo de monitores, SLOs, dashboards e exploração. | Yes |
| Environment/security scope | ✅ | Usuário escolheu multiambiente e zero secrets no core com broker opcional. | Yes |

**Minimum Validations:** 4

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

O API Forge precisa de um control plane agentico e provider-neutral capaz de observar seu próprio runtime e APIs externas, normalizar telemetria, analisar SLO/performance/drift e governar a criação ou alteração de monitores, dashboards, alertas e eventos em ambientes locais, CI, AWS, Kubernetes e VMs.

### Target Users (Draft)

| User | Pain Point |
|------|------------|
| Engenheiro de software | Não sabe se a mudança degradou latência, erros, dependências ou SLO. |
| Engenheiro de plataforma/SRE | Precisa manter observabilidade consistente em vários ambientes e vendors. |
| Engenheiro de dados | Precisa observar APIs e bancos sem perder lineage, custo e qualidade. |
| Agent supervisor | Precisa de fatos canônicos, capacidades, limites e evidências para decidir com segurança. |
| Operador/aprovador | Precisa revisar diff, risco, impacto, rollback e autorização antes de mutar um vendor. |

### Success Criteria (Draft)

- [ ] Um export OTel sintético do Runtime Agentico é normalizado para o contrato canônico com correlação de task, run, agent, tool, trace e span.
- [ ] O mesmo serviço/API produz análise RED/USE e SLO sem inventar throughput, latência, disponibilidade ou causalidade ausentes.
- [ ] Datadog e Dynatrace possuem adapters com capabilities declaradas para consulta, monitores, SLOs, dashboards, eventos e deployment markers.
- [ ] O control plane gera intents e diffs determinísticos para os dois vendors, preservando limitações e divergências.
- [ ] Dry-run é seguro; mutações exigem referência de credencial, policy, aprovação, auditoria e plano de rollback.
- [ ] Agents especialistas podem debater, receber critic e encaminhar divergência para referee/humano.
- [ ] Fixtures sintéticas cobrem sucesso, erro, degradação, cardinalidade, trace quebrado, SLO violado e drift.
- [ ] O caminho local/CI funciona sem credenciais reais, rede ou acesso a vendors.
- [ ] Java, Go e Python recebem recomendações ou artefatos de instrumentação baseados em OTel e contrato da API.

### Constraints Identified

- O core não armazena secrets nem payloads sensíveis por padrão.
- Credenciais externas usam referências e broker opcional com short-lived tokens e least privilege.
- OTel é a abstração padrão; vendor APIs são adapters/capabilities, não o modelo universal.
- Ações de mutação precisam de dry-run, diff, policy, aprovação, evidência e rollback.
- O primeiro CI não depende de exports reais; fixtures sintéticas são obrigatórias.
- Cardinalidade, retenção, custo, rate limits, PII e redaction devem ser tratados como dimensões de primeira classe.

### Out of Scope (Confirmed)

- Auto-remediação autônoma em produção.
- SaaS multi-tenant/UI completa.
- RUM, synthetics, profiler contínuo e matriz infinita de SDKs.
- Paridade forçada entre Datadog e Dynatrace.
- Reconciliação contínua 24/7 sem execução explícita ou CI.

### KB Domains for Define

- `data-quality` — observability, drift, quality dimensions e lineage.
- `genai` — multi-agent, evaluation framework, guardrails e agentic workflow.
- `terraform` — desired state, drift, modules, plan/apply e secrets references.
- `aws` — CloudWatch, X-Ray, ECS, EKS, Lambda, API Gateway e IAM.
- `streaming` — eventos, Kafka/MSK e propagação assíncrona.
- `pydantic`/`python` — contratos, validação, redaction e adapters.
- Conhecimento local: `.claude/skills/api-forge-observability`, `src/apiforge/adapters/otel`, `PerformanceRun`, runtime e fixtures.

### Official References Consulted

- [OpenTelemetry trace semantic conventions](https://opentelemetry.io/docs/specs/semconv/general/trace/)
- [Dynatrace OpenTelemetry integration](https://docs.dynatrace.com/docs/ingest-from/opentelemetry)
- [Dynatrace Service-Level Objectives](https://docs.dynatrace.com/docs/deliver/service-level-objectives)
- [Dynatrace Service-Level Objectives API](https://docs.dynatrace.com/docs/dynatrace-api/environment-api/service-level-objectives-classic)
- [Datadog monitor-based SLOs](https://docs.datadoghq.com/service_level_objectives/monitor/)

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 9 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 4 |
| Duration | 2026-09-22 session |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_FORGE_OBSERVABILITY_CONTROL_PLANE.md`
