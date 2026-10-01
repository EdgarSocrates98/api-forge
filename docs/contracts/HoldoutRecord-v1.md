# HoldoutRecord/v1

Frozen, closed result of a deterministic local mutation.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `mutation_id` | string | yes |
| `target` | string | yes |
| `expected_axis` | `contract`, `security`, `idempotency`, `pagination` | yes |
| `detected` | boolean | yes |
| `evidence` | array[string] | no |
| `limitation` | string or null | no |

Holdouts are applied only to a local sandbox copy. A missed mutation prevents a
verified task from reaching `DONE`.
