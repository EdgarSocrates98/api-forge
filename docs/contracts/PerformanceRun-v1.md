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
