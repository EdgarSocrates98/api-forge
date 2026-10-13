---
name: api-forge-performance
description: >-
  Planeja, gera e interpreta testes de performance de APIs — smoke, baseline,
  load, stress, spike, soak, capacity e failover — e dá veredito
  passed/failed/inconclusive sobre TPS, RPS, concorrência, latência
  p50/p95/p99, erros, saturação, profiling (JFR, pprof, Pyroscope) e regressão
  contra baseline. Use quando houver meta de throughput ou latência, "aguenta
  X TPS?", "ficou mais lento", relatório de
  k6/Locust/JMeter/Gatling/Vegeta/wrk/hey para ler, autoscaling, gargalo,
  custo por transação ou gRPC benchmark. Não use para escolher plataforma (→
  api-forge-architecture) nem para testes funcionais/segurança (→
  api-forge-verification).
compatibility: >-
  Requer o CLI `apiforge`. Geradores (k6, Locust, JMeter, Gatling, Vegeta,
  wrk, hey) e profilers são adapters; o API Forge gera scripts e lê
  relatórios, mas só executa `k6` via `apiforge run tool`, com aprovação para
  alvo remoto.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — performance, carga e capacidade

"Suporta 5.000 TPS" sem cenário, duração, taxa de erro e ponto de saturação
é marketing, não engenharia. Esta skill exige baseline, gerador calibrado e
comparação dentro do noise floor antes de qualquer afirmação.

## Antes de começar

Siga `api-forge-core`. Defina a **transação de negócio** e separe: TPS
(transações de negócio concluídas), RPS (requests recebidos), concorrência e
backlog. Um checkout pode custar 7 requests.

## Procedimento

1. **Plano declarativo** (nunca executa):
   ```text
   apiforge perf plan --subject <svc> --endpoint "POST /orders" --target-tps 200 \
     --test-kind load|stress|spike|soak --duration-s 600 --max-p99-ms 300 --max-error-rate 0.01 --generator k6
   ```
2. **Script do gerador** a partir de um cenário declarado (nunca executa):
   `apiforge perf scenario --tool k6|jmeter|locust --scenario scenario.json`.
3. **Registre o contexto da execução:** commit, infraestrutura, dataset,
   payload, warmup, ramp, hold, cooldown, região do gerador.
4. **Execute fora do core** (ou `apiforge run tool k6 --target <script> --out <summary.json>`
   com `--approve` se o alvo for remoto). Calibre o gerador: se ele saturar
   CPU/rede, o resultado é `inconclusive`.
5. **Leia o relatório:**
   `apiforge model k6|locust|jmeter|gatling|vegeta|wrk|hey|pytest-benchmark --path <relatório>`;
   traces: `apiforge model otel --path <otlp.json>`; profiling:
   `apiforge model jfr|pprof|pyroscope --path <perfil>`.
6. **Meça o conjunto:** p50/p95/p99, erros, 429, timeouts, CPU, memória, GC,
   pools, banco, cache, filas, consumer lag e custo.
7. **Veredito e regressão:**
   ```text
   apiforge perf verdict --run <run.json> [--repeat-baseline <dir-baselines>]
   apiforge perf compare --baseline <a.json> --candidate <b.json> --threshold-pct 10 --repeat-baseline <dir>
   ```
   Delta dentro do noise floor medido é `inconclusive`, não ganho.
8. **Sugestão** como ActionPlan (nunca aplicada): `apiforge perf suggest`.
   Uma variável por experimento; reexecute o mesmo cenário e compare.
9. **Histórico:** `apiforge perf memory` guarda PerformanceRuns append-only.
   gRPC: `apiforge grpc benchmark` recusa capacidade de execuções inválidas.

## Resultado

`passed`, `failed`, `inconclusive`, `blocked` ou `unsafe_to_run`. Separe
`mechanism_confirmed` (o mecanismo existe) de `runtime_certified` (medido
sob carga). Nunca afirme "suporta X TPS" sem cenário, duração, taxa de
sucesso, erro, ponto de saturação e limites.

## Guardrails

- Não rode carga contra produção nem contra alvo remoto sem aprovação
  registrada.
- Não extrapole: 100 TPS medidos não implicam 1.000 com 10× instâncias.
- Não compare execuções não equivalentes (dataset, infra ou warmup
  diferentes).
- Não declare regressão ou ganho sem `min-samples` e noise floor.

## Entrega

Plano, script gerado, contexto da execução, PerformanceRun, veredito com
condições nomeadas, comparação com baseline, gargalo identificado com
evidência e ActionPlan para a próxima iteração.

Especialistas típicos: `api-load-capacity-engineer` (cenários e veredito de
TPS), `api-performance-engineer` (tuning e profiling).
