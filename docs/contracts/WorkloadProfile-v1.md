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
| `max_request_duration_s` | number|null | no |
| `max_payload_bytes` | integer|null | no |
| `needs_os_control` | boolean|null | no |
| `needs_kubernetes` | boolean|null | no |
| `team_maturity` | enum|null | no |
| `data_model` | enum|null | no |

Declared workload shape for architecture comparison. Every dimension is
declared by the plan's author — the profile is a planning artifact,
never inferred from telemetry. Absent dimensions stay `null` and are
named, not defaulted.

Closed vocabularies: `timing` = `synchronous|asynchronous`,
`arrival` = `bursty|steady`, `state` = `stateless|stateful`,
`bound` = `cpu|io`, `scope` = `regional|global`,
`exposure` = `public|private`, `team_maturity` = `low|medium|high`,
`data_model` = `key-value|document|graph|relational|cache`.

The last six fields feed the Architecture Decision Engine
(`plan architecture`): `max_request_duration_s` disqualifies Lambda above
900s, `needs_os_control`/`needs_kubernetes` eliminate the candidates
that cannot satisfy them, `team_maturity` weights operational
complexity, and `data_model` decides which datastore role is evaluated
— without it, every datastore is rejected as "not evaluated", never
guessed.
