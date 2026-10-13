# ActionPlan/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `steps` | array | yes |
| `risk` | ActionRisk | no |
| `rollback` | string | no |
| `requires_approval` | boolean | no |
| `status` | string | no |

A proposed sequence of verbs — a suggestion, never auto-applied.
