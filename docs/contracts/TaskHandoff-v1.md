# TaskHandoff/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `task_id` | string | yes |
| `revision` | integer | yes |
| `from_agent` | string | yes |
| `to_executor` | string | yes |
| `context` | array | no |
| `dispatched_at` | string|null | no |

A recorded dispatch: who handed what context to which executor.
