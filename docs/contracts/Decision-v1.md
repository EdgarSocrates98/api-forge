# Decision/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `summary` | string | yes |
| `status` | DecisionStatus | no |
| `decided_by` | string|null | no |
| `evidence` | array | no |
| `supersedes` | string|null | no |
| `rationale` | string | no |

A recorded decision: what was chosen, by whom, on which evidence.
