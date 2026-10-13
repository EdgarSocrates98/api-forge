# Receipt/v1

Frozen, closed (`extra: forbid`). Canonical contract — see
`src/apiforge/contracts/` for the model and `tests/contracts/` for
conformance tests.

| Field | Type | Required |
|---|---|---|
| `schema_version` | string | no |
| `proves` | string | no |
| `case` | string | yes |
| `policy_sha256` | string | yes |
| `artifacts` | array | yes |
| `input_hashes` | array | no |
| `emitted_at` | string|null | no |


