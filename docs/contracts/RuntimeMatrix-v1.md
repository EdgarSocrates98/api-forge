# RuntimeMatrix/v1

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
| `verified_on` | string|null | no |
| `constraints` | object | no |

Versioned runtime constraints; entries land with each knowledge pack.
