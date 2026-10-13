# PerformanceRun/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `produced_by` | string | no |
| `unresolved` | array | no |
| `attributes` | object | no |
| `subject` | string | no |
| `duration_ms` | number|null | no |
| `baseline_ref` | string|null | no |
| `test_kind` | enum|null | no |
| `target_tps` | number|null | no |
| `achieved_tps` | number|null | no |
| `successful_tps` | number|null | no |
| `failed_tps` | number|null | no |
| `rps_received` | number|null | no |
| `rps_processed` | number|null | no |
| `tps_completed_transactions` | boolean|null | no |
| `p50_ms` | number|null | no |
| `p95_ms` | number|null | no |
| `p99_ms` | number|null | no |
| `max_latency_ms` | number|null | no |
| `error_rate` | number|null | no |
| `http_4xx_rate` | number|null | no |
| `http_5xx_rate` | number|null | no |
| `http_429_rate` | number|null | no |
| `timeout_rate` | number|null | no |
| `duplicates_detected` | boolean|null | no |
| `cpu_percent` | number|null | no |
| `memory_percent` | number|null | no |
| `gc_pause_ms` | number|null | no |
| `connection_pool_usage` | number|null | no |
| `database_latency_ms` | number|null | no |
| `cache_hit_rate` | number|null | no |
| `queue_lag` | number|null | no |
| `consumer_lag` | number|null | no |
| `cold_starts` | number|null | no |
| `cost_per_transaction` | number|null | no |
| `test_duration_s` | number|null | no |
| `warmup_duration_s` | number|null | no |
| `min_duration_s` | number|null | no |
| `ramp_profile` | string|null | no |
| `payload_profile` | string|null | no |
| `environment` | string|null | no |
| `commit_sha` | string|null | no |
| `infrastructure_revision` | string|null | no |
| `downstreams_observed` | boolean|null | no |
| `generator_dropped_iterations` | integer|null | no |
| `slo_error_rate` | number|null | no |
| `slo_p99_ms` | number|null | no |

A measured load/performance run. Every metric is optional: `null` is
*measured absence* — the run did not report the value — never a zero.

`test_kind` is a closed vocabulary declared by the run's author:
`smoke | baseline | load | stress | spike | soak | capacity | failover |
chaos` — never inferred from the numbers.

**RPS and TPS are distinct.** `rps_*` counts HTTP requests; `*_tps`
counts business transactions. A run declares
`tps_completed_transactions: true` only when its TPS metric provably
counts completed transactions — "supported X requests" is not "supports
X TPS".

**Verdict** (`apiforge perf verdict --run <run.json>`): `passed` only
when every validity condition (baseline, environment, reproducibility,
target reached, generator not saturated, downstreams observed, TPS is
completed transactions) **and** every performance condition (error rate
and p99 within declared SLOs, no duplicate transactions) is met.
Unevaluable conditions — fields the run never reported — make the
verdict `inconclusive` and are named, never guessed. `blocked`,
`skipped_with_reason`, `unsafe_to_run`, `not_applicable` are declared by
the run's producer, not computed.

**OTel producer** (`apiforge model otel --path <export.json>`):
`subject` = `service.name` resource attribute (empty + `unresolved` when
absent), `duration_ms` = wall span of the export, `attributes.operations`
= per-operation `{count, mean_ms, p95_ms, max_ms}` (nearest-rank
percentiles, deterministic). `perf compare` consumes two of these
payloads; `baseline_ref` stays unset at ingest and is filled by
composition, never guessed.
