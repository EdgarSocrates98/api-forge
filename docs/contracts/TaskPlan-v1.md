# TaskPlan/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `task_id` | string | yes |
| `revision` | integer | yes |
| `recipe` | Recipe | yes |
| `steps` | array | no |
| `plan_digest` | SHA-256 string | no |
| `proof_axes` | array[string] | no |

The recipe instantiated for a task — ordered verbs with bound inputs.
