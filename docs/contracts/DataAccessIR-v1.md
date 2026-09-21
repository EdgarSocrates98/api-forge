# DataAccessIR/v1

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
| `database` | string | no |
| `provider` | string | no |
| `entities` | array | no |
| `access_patterns` | array | no |

Data-access intermediate representation; per-database fields land
