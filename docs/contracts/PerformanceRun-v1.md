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

A measured run; metrics and noise-floor fields land with perf layer.

**OTel producer** (`apiforge model otel --path <export.json>`):
`subject` = `service.name` resource attribute (empty + `unresolved` when
absent), `duration_ms` = wall span of the export, `attributes.operations`
= per-operation `{count, mean_ms, p95_ms, max_ms}` (nearest-rank
percentiles, deterministic). `perf compare` consumes two of these
payloads; `baseline_ref` stays unset at ingest and is filled by
composition, never guessed.
