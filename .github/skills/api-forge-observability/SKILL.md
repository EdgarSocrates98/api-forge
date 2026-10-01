---
name: api-forge-observability
description: >-
  Projeta e revisa a telemetria e a operação de APIs — logs, métricas, traces,
  RED/USE, SLI/SLO, error budget, alertas, dashboards e runbooks — com
  OpenTelemetry como contrato canônico e Datadog, Dynatrace, CloudWatch e
  X-Ray como projeções de vendor. Use para instrumentar um serviço (Java, Go,
  Python), "como saberíamos que isso está quebrando?", correlacionar
  trace/log, definir SLOs, revisar alertas ruidosos, planejar leitura de
  vendor sem credencial, preparar incidente ou avaliar readiness operacional e
  modos de autonomia/runbooks. Não use para medir capacidade sob carga (→
  api-forge-performance) nem para desenhar timeouts/retries (→
  api-forge-verification).
compatibility: >-
  Offline-first; requer o CLI `apiforge`. Datadog, Dynatrace e CloudWatch são
  adapters: o core gera planos de leitura e valida metadados de credencial sem
  ler ambiente nem secret store. Não captura payloads sensíveis por padrão.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — observabilidade e operação

Observabilidade é a capacidade de responder a uma pergunta nova sobre
produção sem fazer deploy. Ausência de alerta não é ausência de falha; por
isso esta skill começa pelas perguntas operacionais e só depois escolhe
sinais e backend.

## Antes de começar

Siga `api-forge-core`. Liste as operações críticas (do API-IR) e o SLO de
cada uma; sem SLO, alertas viram ruído.

## Procedimento

1. **Sinais por operação:** tráfego, erros, latência e saturação (RED para
   requests, USE para recursos).
2. **Instrumentação recomendada** por linguagem/framework:
   ```text
   apiforge observability instrument --language java|go|python [--framework <fw>]
   ```
   Cubra servidor, cliente HTTP, SDK AWS, banco, cache, Kafka/filas e
   retries; propague `trace_id`, `span_id`, `correlation_id`, revision,
   route, method e status.
3. **Redação:** secrets, tokens, PII, `Authorization` e payloads sensíveis
   nunca entram em log, atributo de span ou métrica.
4. **Ingestão e saúde sobre fixtures/exports** (sem acesso externo):
   ```text
   apiforge observability ingest --source <otel.json> [--service <s>] [--slo slo.json]
   apiforge observability health --source <otel.json> --service <s> [--slo slo.json]
   apiforge model otel --path <otlp.json>                 # vira perf.otel.* facts
   ```
   AWS: `apiforge collect cloudwatch --alarm-prefix <p> --out <dump> --now <ISO>`
   ou `apiforge collect xray --out <dump> --now <ISO>` →
   `apiforge model cloudwatch|xray --path <dump>`.
5. **Vendor sem credencial no core:**
   ```text
   apiforge observability capabilities
   apiforge observability read-plan --provider otel|datadog|dynatrace|cloudwatch --service <s> --start <ISO> --end <ISO> [--signal traces|metrics|logs|events]
   apiforge observability credential-check ...
   ```
   Antes de qualquer leitura live: `apiforge evidence gate --question "..."`.
6. **SLO → alerta → runbook:** cada alerta tem SLI, limiar ligado ao error
   budget (burn rate), dono e runbook acionável.
7. **Diagnóstico:** a telemetria precisa distinguir gateway, aplicação,
   banco, cache, rede e consumidor; se não distingue, é gap.
8. **Registre** sampling, retenção, custo, atraso de ingestão e gaps.
9. **Operação governada:** `apiforge autonomy status` mostra o modo
   (observe → continuous); `autonomy runbook` e `autonomy heal` executam só
   o que a policy permite e registram tudo no ledger (`autonomy ledger`).

## Guardrails

- Logs não substituem traces; métricas não substituem ambos.
- Não crie alerta sem ação operacional e dono.
- Ausência de evento não prova ausência de falha (sampling, perda, atraso).
- Nenhum backend (X-Ray, Datadog, Dynatrace) é o modelo universal; OTel é o
  contrato, vendor é projeção.
- Não mude o modo de autonomia sem aprovação — a própria mudança é ação
  gated pela policy.

## Entrega

Telemetry contract por operação, matriz RED/USE, SLI/SLO e error budget,
alertas com burn rate, dashboards, runbooks, plano de leitura de vendor e
gaps de observabilidade.

Especialistas típicos: `api-observability-engineer` (instrumentação e SLO),
`api-observability-integration-engineer` (Datadog/Dynatrace),
`api-operations-engineer` (autonomia e runbooks).
