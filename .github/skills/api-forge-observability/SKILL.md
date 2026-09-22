---
name: api-forge-observability
description: Projeta e revisa logs, métricas, traces, SLOs, dashboards, alertas e runbooks de APIs. Use para OTel, ADOT, CloudWatch, Prometheus, Grafana, X-Ray, correlação distribuída, debugging, incidentes e readiness operacional.
compatibility: Prefira OpenTelemetry/ADOT como abstração; backends AWS ou self-hosted são adapters. Não capture payloads sensíveis por padrão.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Defina sinais por operação: tráfego, erros, latência e saturação.
2. Propague correlation_id, trace_id, span_id, revision, route, method e status.
3. Instrumente servidor, cliente HTTP, AWS SDK, banco, cache, Kafka, filas e retries.
4. Redija secrets, tokens, PII, authorization headers e payloads sensíveis.
5. Relacione sinais a SLI/SLO, alertas, ownership e runbooks.
6. Verifique se a telemetria permite distinguir gateway, aplicação, banco, cache, rede e consumidor.
7. Registre sampling, retenção, custo, atraso e gaps de observabilidade.

## Não faça

- não use logs como substituto de traces;
- não crie alerta sem ação operacional;
- não confunda ausência de evento com ausência de falha;
- não trate X-Ray ou qualquer backend como modelo universal.

## Entrega

Entregue telemetry contract, matriz RED/USE, SLO/SLI, dashboards, alertas, runbooks e gaps.

