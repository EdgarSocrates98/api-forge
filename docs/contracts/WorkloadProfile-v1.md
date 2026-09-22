# WorkloadProfile/v1

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
| `timing` | enum|null | no |
| `arrival` | enum|null | no |
| `state` | enum|null | no |
| `bound` | enum|null | no |
| `latency_sensitive` | boolean|null | no |
| `throughput_sensitive` | boolean|null | no |
| `event_driven` | boolean|null | no |
| `batch` | boolean|null | no |
| `streaming` | boolean|null | no |
| `multi_tenant` | boolean|null | no |
| `scope` | enum|null | no |
| `exposure` | enum|null | no |

Declared workload shape for architecture comparison. Every dimension is
declared by the plan's author — the profile is a planning artifact,
never inferred from telemetry. Absent dimensions stay `null` and are
named, not defaulted.

Closed vocabularies: `timing` = `synchronous|asynchronous`,
`arrival` = `bursty|steady`, `state` = `stateless|stateful`,
`bound` = `cpu|io`, `scope` = `regional|global`,
`exposure` = `public|private`.
