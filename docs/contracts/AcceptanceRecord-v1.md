# AcceptanceRecord/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `task_id` | string | yes |
| `revision` | integer | yes |
| `verdict` | string | yes |
| `accepted_by` | string | yes |
| `executed_by` | string|null | no |
| `evidence` | array | no |
| `notes` | string | no |

Acceptance — recorded by an identity distinct from the executor.
