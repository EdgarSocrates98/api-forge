# TelemetryEvent/v1

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
| `name` | string | no |
| `observed_at` | string|null | no |

OTel-shaped event; full span/metric fields land with the telemetry layer.
