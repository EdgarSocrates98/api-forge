---
name: api-forge-performance
description: Planeja e interpreta benchmarks, load tests, stress tests, spike, soak, capacity, TPS, RPS, latência, saturação e regressões de APIs. Use quando houver metas de throughput, p95/p99, autoscaling, gargalos, custo por transação ou validação de performance.
compatibility: Pode integrar k6, Locust, JMeter, Gatling, Vegeta, wrk, pprof, JFR, async-profiler, pytest-benchmark, CloudWatch, Prometheus e OTel como adapters.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Defina a transação de negócio e diferencie TPS, RPS, concorrência e backlog.
2. Registre baseline, commit, infraestrutura, dataset, payload, warmup, ramp, hold e cooldown.
3. Calibre o gerador; se ele saturar, marque o resultado como `inconclusive`.
4. Meça p50, p95, p99, erros, 429, timeouts, CPU, memória, GC, pools, banco, cache, filas, consumer lag e custo.
5. Execute testes separados: smoke, baseline, load, stress, spike, soak, capacity, failover e chaos.
6. Compare execuções equivalentes e estime o noise floor antes de afirmar regressão ou ganho.
7. Separe `mechanism_confirmed` de `runtime_certified`.
8. Gere recomendação como diff ou ActionPlan; nunca aplique automaticamente.
9. Reexecute o cenário após a mudança e compare com o baseline.

## Resultado

Use `passed`, `failed`, `inconclusive`, `blocked` ou `unsafe_to_run`. Nunca afirme “suporta X TPS” sem explicar cenário, duração, sucesso, erro, saturação e limites.

