# TestRecord/v1

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
| `kind` | enum|null | no |
| `state` | enum|null | no |
| `objective` | string|null | no |
| `scenario` | string|null | no |
| `inputs` | array | no |
| `environment` | string|null | no |
| `tool` | string|null | no |
| `tool_version` | string|null | no |
| `duration_s` | number|null | no |
| `data_used` | string|null | no |
| `metric` | string|null | no |
| `threshold` | string|null | no |
| `evidence` | array | no |
| `limitations` | array | no |
| `reproducible` | boolean|null | no |
| `reason` | string|null | no |

One executed test in the risk-based strategy. `kind` is the closed
21-value taxonomy: `lint`, `typecheck`, `unit`, `component`,
`integration`, `contract`, `consumer_contract`, `e2e`, `property`,
`fuzz`, `mutation`, `security`, `load`, `stress`, `spike`, `soak`,
`capacity`, `failover`, `chaos`, `recovery`, `cost`.

`state` is the closed 7-value vocabulary: `passed`, `failed`,
`inconclusive`, `blocked`, `skipped_with_reason`, `unsafe_to_run`,
`not_applicable`. A record is never "passed by absence of error" —
`passed` means the declared metric was produced and met its threshold.
Every field is optional; `null`/empty means *not recorded*, never zero.
`reason` carries the why for `blocked`, `skipped_with_reason`,
`unsafe_to_run` and `not_applicable`.
